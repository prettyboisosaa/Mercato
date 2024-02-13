# Mercato

Socket-Based Market System

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Credits](#credits)
- [Badges](#badges)

## Description

This project implements a simple socket-based market system where buyers and sellers can interact to buy and sell products. The system allows users to choose between buying or selling, list available products, and negotiate prices. Sellers can add/change their products and buyers can initiate negotiations.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prettyboisosaa/Mercato.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Mercato
   ``` 
5. Run the server (in one terminal):
   ```bash
   python server_mercato.py
   ```
7. Run a client (in another terminal):
   ```bash
   python client_mercato.py
   ```
Note: it is recommended to run multiple clients to ensure enough members to initiate negotiations
## Usage
### Buyer Client:
 - Connect to the server by running the client script.
 - Choose to buy and follow the prompts to select products and sellers.
 - Initiate negotiations and enter integer values to negotiate prices.
### Seller Client:
 - Connect to the server by running the client script.
 - Choose to sell and manage your products. Add/change products or delete existing ones.
 - Wait for buyers to initiate negotiations and respond accordingly.

Please note: The negotiation process involves exchanging integer values to agree on prices. Make sure to follow the prompts during negotiations.

## Credits
[Leitos](https://github.com/LeitosRoncio)
[Sosa](https://github.com/prettyboisosaa)
[Sartoz](https://github.com/frakizan)
[Fonji](https://github.com/Jonjiwjk)

## Badges

[![Example Badge](example-badge-link)](link-to-related-tool)

