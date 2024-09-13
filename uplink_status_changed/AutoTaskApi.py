import requests, json, re, os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MakeAutoTaskApiCall:
    
    def __init__(self):  

        # queryFilter variables to perform the GET
        cliente = 'EMPRESA' # serach company name from the ticket title
        incidente = 'Uplink status changed'
        fila = ''
        queryFilter = '{"filter": [{"op": "contains","field": "title", "value" :"'+cliente+'" }, {"op": "contains","field": "title", "value" :"'+incidente+'" }, {"op": "noteq", "field": "status", "value": "5"}]}'
        
        # concatenates the standard http link with the filter
        self.baseUrl = 'https://webservices3.autotask.net/atservicesrest/v1.0/tickets'
        self.api = self.baseUrl + "/query?search=" + queryFilter
        
        # parameters to perform the get
        self.parameters = {
            "ApiIntegrationCode": os.getenv("AUTOTASK_API_INTEGRATION_CODE"),
            "UserName": os.getenv("AUTOTASK_USER_NAME"),
            "Secret": os.getenv("AUTOTASK_SECRET"),
            "Content-Type": "application/json"     
        }
     
    # returns the list of open tickets according to the specifications in the class init              
    def get_ticket_list(self):
        # GET API
        response = requests.get(self.api, headers=self.parameters)
        
        if response.status_code == 200:
            json_tree = json.loads(response.text)
            ticket_list = json_tree['items']
            return ticket_list
        else:
            print(f'Request failed {response.status_code}')
    
    # searches for the device name within the ticket description            
    def get_device_name(self, ticket_list):
            # auxiliary variables
            device_name_list = []
            aux = 0
            # searches for the device name within the description and assigns it to a list
            for items in ticket_list:
                desc = str(ticket_list[aux]['description'])
                patternDevice = re.compile(r'EMPRESA-[a-zA-Z]{1,2}-[a-zA-Z]{1,100}-?[a-zA-Z]{1,100}-?[a-zA-Z]{1,100}-?[a-zA-Z]{1,100}-?[a-zA-Z]{1,100}')
                device_name = re.search(patternDevice, desc)
                device_name_list.append(device_name.group())
                aux += 1  
            return device_name_list

    # Function that checks if there is a ticket file in the lock folder and starts the process
    def verificaLock(self, ticket_list):
        
        # Load data from JSON
        json_data = ticket_list

        # Create the lock folder if it does not exist
        if not os.path.exists("lock"):
            os.mkdir("lock")

        # Iterate over the items in the array
        for item in json_data:
            ticketID = item['id']
            ticket_number = item["ticketNumber"]

            # Check if the file with the ticket name exists in the lock folder
            if os.path.isfile('lock/' + item['ticketNumber'] + '.txt'):
                print(f'O atendimento do ticket {item["ticketNumber"]} já está em andamento.\n')
                return '1'
            else:
                with open(f"lock/{ticket_number}.txt", "w") as f:
                    f.write(f'Este arquivo corresponde ao ticket = {ticket_number}\nID do ticket = {ticketID}')
             
                # Redirect ticket to the automation queue
                redirectAuto = {
                    "id": ticketID,
                    "status": 8,
                    "queueID": 29688711
                }
                putRequest = requests.request('PATCH', f"{self.baseUrl}", headers=self.parameters, data=json.dumps(redirectAuto))
                if putRequest.status_code == 200:
                    print(f"Chamado {ticket_number} redirecionado para a fila de automação")
                else:
                    print("Erro ao redirecionar chamado para a fila de monitoração")
                    print(putRequest.content)
     
    # Function for closing a ticket in AutoTask              
    def encerraChamado(self, ticket_id, ticket_number, link, device, status):
        
        # Path to the ticket in the lock folder
        lockTicket = f'lock/{ticket_number}.txt'
        
        # Parameters for request
        apiMethod = 'PATCH'
        
        resolutionOK = {
            "id": ticket_id,
            "status": "5",
            "Activity": f'Foi dectado apenas uma oscilação nas interfaces do device {device}. \nEvidências:{link} \nChamado encerrado.',
            "resolution": f'Foi dectado apenas uma oscilação nas interfaces do device {device}. \nEvidências:{link} \nChamado encerrado.'
        }
        
        resolutionNOK = {
            "id": ticket_id,
            "queueID": 8,
            "resolution": f'A(s) interface(s) do device {device} permanecem inoperantes, chamado redirecionado para a fila da monitoração.'
        }
        
        if status != 'ok':
            print(f"As interfaces do device {device} permanecem inoperantes.\n")
            putRequest = requests.request(apiMethod, f"{self.baseUrl}", headers=self.parameters, data=json.dumps(resolutionNOK))
        else:
            print("Houve apenas uma oscilação no link, encerrando chamado...\n")
            
            # API patch request
            putRequest = requests.request(apiMethod, f"{self.baseUrl}", headers=self.parameters, data=json.dumps(resolutionOK))
            
            # Check request status
            if putRequest.status_code == 200:                
                # Delete .lock file after the procedure is successfully completed
                try:
                    os.remove(lockTicket)
                    print(f'Arquivo {lockTicket}.txt deletado com sucesso\n')
                except FileNotFoundError:
                    print(f"Erro: Arquivo {lockTicket} não encontrado.\n")
            else:
                print(f'Request failed {putRequest.content}\n')
                
    # returns the received JSON formatted and indented
    def parse_json(self, obj):
        formatted_json = json.dumps(obj, indent=2)
        return formatted_json