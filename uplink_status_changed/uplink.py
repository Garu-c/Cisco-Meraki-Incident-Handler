import meraki, time, os
from datetime import datetime
from AutoTaskApi import MakeAutoTaskApiCall
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the Meraki API key from environment variables
API_KEY = os.getenv('MERAKI_API_KEY')

def main():
    print('\nServiço Iniciado')
    
    # Instantiate the AutoTask API session
    at_call = MakeAutoTaskApiCall()
    # Ticket variables
    fmt = at_call.parse_json
    ticket_list = at_call.get_ticket_list()
            
    # Instantiate the Meraki API session
    dashboard = meraki.DashboardAPI(
        api_key=API_KEY,
        base_url='https://api.meraki.com/api/v1/',
        output_log=False,
        print_console=False,
        suppress_logging=True
    )
    
    # Store all the organizations that the API key has access to
    organizations = dashboard.organizations.getOrganizations()
    org = organizations[0]
    orgId = org['id']
        
    # Try to validate the status of the devices, if the API returns an error the ticket is forwarded to the NOC
    try:
        # Get basic info of all devices (serial, id, status, etc.)
        devices_status = dashboard.organizations.getOrganizationDevicesAvailabilities(orgId, -1)
        
        device = dashboard.organizations.getOrganizationDevices(orgId)
        
        for i in device:
            if i['name'] == 'NOME_DEVICE':
                serial = i['serial']
                # print(fmt(i))
                                                    
        print(f'\nAnalisando devices da rede {netName} - {orgName}:')
        checked_list = check_device_status(tckt_hostname_list, devices_status)
        online = fmt(checked_list[0])
        offline = fmt(checked_list[1])
        print(f'\nDevices online: {online}')
        print(f'\nDevices offline: {offline}')
        
        if offline == 0:
            print('Todos os devices estão online')
            
        else:
            print('\nUm ou mais devices permanecem offline\nIniciando validação de 1 em 1 minuto')
            for i in range(5):
                time.sleep(5)
                print(f'\nTentativa {i+1} de 5')
                checked_list = check_device_status(tckt_hostname_list, devices_status)
                online = fmt(checked_list[0])
                offline = fmt(checked_list[1])
                print(f'\nDevices online: {online}')
                print(f'\nDevices offline: {offline}')
            
            if i == 4:
                print('\nEncaminhando chamado para o noc')
        
    except meraki.APIError as e:
        if e.status == 403:
            print('\nLicença para consulta via API Meraki expirada, não foi possível fazer a validação do(s) equipamento(s)\n')
            print(e)
        else:
            print(f'\nErro Meraki API {e}')

def get_org_and_network_by_ticket_net_name(dashboard, organizations, tckt_desc):
    '''Returns the organization and network based on the network name received in the ticket'''
    for org in organizations:
        orgApi = org['api']['enabled']
        if orgApi == True:
            organizationId = org['id']
            networks = dashboard.organizations.getOrganizationNetworks(organizationId)
            
            for net in networks:
                networkName = net['name']
                if networkName in tckt_desc:
                    print(networkName)
                    organization = org
                    network = net
                    
    return organization, network
    
def check_device_status(tckt_hostname_list, devices_status):
    '''Receives a list of hostnames and the list of Meraki devices. Validation is done for each device, returns the list of validated devices'''
    # List to store offline devices
    off_list = []
    on_list = []
    for hostname in tckt_hostname_list:
        for device in devices_status:
            # Validate if the keys 'name' and 'status' exist for the device
            try:
                name = device['name']
                status = device['status']
            except KeyError as key:
                # print(f'Key not found {key}')
                continue
            if name == hostname:
                if status == 'online':
                    on_list.append(device)
                else:
                    print(f'\nDevice {name} offline, encaminhando chamado para o NOC...')
                    off_list.append(device)
                    
    return on_list, off_list

if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f'\nScript concluído, total runtime {end_time - start_time}\n')