from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# Endpoint for bin collection data
@app.route('/bin-collections', methods=['POST'])
def get_bin_collection():
    try:
        # Parse JSON body
        data = request.get_json()
        postcode = data.get('postCode')
        street_name = data.get('street')
        house_number = data.get('houseNumber')
        area = data.get('area')

        # Validate input
        if not all([postcode, street_name, house_number, area]):
            return jsonify({"error": "All fields (postCode, street, houseNumber, area) are required."}), 400

        # Construct the house string based on input
        house = f"{house_number}  {street_name.upper()} {area.upper()}"

        # URL for the initial form submission
        initial_url = "https://www.sefton.gov.uk/bins-and-recycling/bins-and-recycling/when-is-my-bin-collection-day/"
        
        # Start a session to manage cookies and maintain the session state
        session = requests.Session()

        # Fetch the initial page to get any necessary hidden tokens
        response = session.get(initial_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting the hidden tokens from the form
        request_verification_token = soup.find("input", {"name": "__RequestVerificationToken"})['value']
        ufprt_token = soup.find("input", {"name": "ufprt"})['value']

        # Prepare the data payload for the first form submission
        form_data = {
            "Postcode": postcode,
            "Streetname": street_name,
            "__RequestVerificationToken": request_verification_token,
            "ufprt": ufprt_token
        }

        # Submit the form
        response = session.post(initial_url, data=form_data)

        # Check if the form submission was successful
        if response.status_code == 200:
            # Parse the response from the form submission
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the address selection form
            address_form = soup.find("form", {"action": "/bins-and-recycling/bins-and-recycling/when-is-my-bin-collection-day/"})
            if address_form:
                # Extract the hidden tokens again (they might change for each step)
                request_verification_token = address_form.find("input", {"name": "__RequestVerificationToken"})['value']
                ufprt_token = address_form.find("input", {"name": "ufprt"})['value']

                # Find the select element with the addresses
                select = address_form.find("select", {"name": "selectedValue"})
                # Find the specific option value (select the one that matches your house number)
                selected_option = select.find("option", string=lambda x: x and house in x)
                if selected_option:
                    selected_value = selected_option['value']

                    # Prepare the data payload for the second form submission
                    form_data = {
                        "selectedValue": selected_value,
                        "Action": "Select",
                        "__RequestVerificationToken": request_verification_token,
                        "ufprt": ufprt_token
                    }

                    # Submit the second form
                    final_response = session.post(initial_url, data=form_data)

                    # Check if the submission was successful
                    if final_response.status_code == 200:
                        # Parse the final response page containing the tables
                        final_soup = BeautifulSoup(final_response.text, 'html.parser')
                        # Find all tables with the specified class and summary
                        tables = final_soup.find_all("table", {"class": "table table-striped table-bordered", "summary": "details of domestic refuse collections"})
                        
                        # Container for the results
                        result = []

                        if tables:
                            # Iterate through each table and extract information
                            for table in tables:
                                # Extract table rows
                                rows = table.find("tbody").find_all("tr")
                                for row in rows:
                                    # Extract cells
                                    cells = row.find_all("td")
                                    # Determine the bin type color based on the bin description
                                    bin_description = cells[0].text.strip()
                                    if "Green 240 wheelie bin" in bin_description:
                                        bin_type = "green"
                                    elif "Residual 240 wheelie bin" in bin_description:
                                        bin_type = "grey"
                                    elif "Recycling 240 wheelie bin" in bin_description:
                                        bin_type = "brown"
                                    else:
                                        bin_type = "unknown"  # Default if none match

                                    # Get the next collection date and calculate days until next collection
                                    next_collection_date_str = cells[2].text.strip()
                                    next_collection_date = datetime.strptime(next_collection_date_str, "%d/%m/%Y")
                                    today = datetime.now().date()
                                    
                                    # Calculate the difference in days
                                    days_until_next_collection = (next_collection_date.date() - today).days + 1

                                    # Structure the data as a dictionary
                                    bin_data = {
                                        "binType": bin_type,
                                        "collectionDay": cells[1].text.strip(),
                                        "nextCollectionDate": next_collection_date_str,
                                        "daysUntilNextCollection": days_until_next_collection
                                    }
                                    # Append the dictionary to the result list
                                    result.append(bin_data)
                            
                            # Return the result as a JSON response
                            return jsonify(result)
                        else:
                            return jsonify({"error": "No tables found with the specified criteria on the final page."}), 404
                    else:
                        return jsonify({"error": "Error submitting the address selection form."}), 500
                else:
                    return jsonify({"error": "Specified house number not found in the dropdown options."}), 404
            else:
                return jsonify({"error": "Address selection form not found on the page."}), 404
        else:
            return jsonify({"error": "Error submitting the initial form."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
