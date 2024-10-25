# Sefton Council Bin Collection API

This project is a Flask-based API that allows you to get the bin collection dates from Sefton Council for your house.

## Prerequisites

- **Docker**: Make sure you have Docker installed on your system.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/tom-murray/sefton-bin-collection.git
cd sefton-bin-collection
```

2. Create a requirements.txt file (if not already present) with the following content:

```
Flask==2.3.3
requests==2.31.0
BeautifulSoup==4.12.3
```

## Building the Docker Image

Build the Docker image using the following command:

```bash
docker build -t sefton-bin-collection-api .
```

This command creates a Docker image named sefton-bin-collection-api.

## Running the Docker Container

Run the Docker container:

```bash
docker run -d -p 5000:5000 --name sefton-bin-collection sefton-bin-collection-api
```

If port 5000 is already in use, you can map the container to a different port:

```bash
docker run -d -p 5001:5000 --name sefton-bin-collection sefton-bin-collection-api
```

## API Usage

### Endpoint

POST /bin-collections

### Request Body

{
"postCode": "LXX 8XX",
"street": "Some Street",
"houseNumber": "25",
"area": "Some Area"
}

### Response

The API will respond with a JSON object:

```json
[
  {
    "binType": "green",
    "collectionDay": "Monday",
    "nextCollectionDate": "28/10/2024",
    "daysUntilNextCollection": 4
  },
  {
    "binType": "grey",
    "collectionDay": "Tuesday",
    "nextCollectionDate": "29/10/2024",
    "daysUntilNextCollection": 5
  },
  {
    "binType": "brown",
    "collectionDay": "Tuesday",
    "nextCollectionDate": "05/11/2024",
    "daysUntilNextCollection": 12
  }
]
```

## License

Feel free to take my code and amend as you desire.
