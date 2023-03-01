import sys
import os
import time


## importa classes
from environment import Env
from explorer import Explorer
from rescuer import Rescuer

def main():
    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder_name = 'data'
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))

    
    # Instantiate the environment
    env = Env(data_folder)
    
    # config files for the agents
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file = os.path.join(data_folder, "explorer_config.txt")
    
    # Instantiate agents rescuer and explorer
    resc = Rescuer(env, rescuer_file)

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    exp = Explorer(env, explorer_file, resc)

    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    main()