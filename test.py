
for key, inner_dict in dic_all.items():
    print("Step ID: {}".format(key))
    for param_name, param_info in inner_dict.items():
        print("  {}:".format(param_name))
        for param_key, param_value in param_info.items():

            if param_value.imagename == 'ReportText':
                print(" {}:".format(param_value.filenamelong))
            elif param_value.valuemean == None or param_value.valuemean == null:
                print(" {}:".format(param_value.valuestring))
            else:
                print(" {}:".format(param_value.valuemean))

            if param_value.units != 'NA':
                print(" {}:".format(param_value.units))
            else:
                print("")
            
            if param_value.specmin != None:
                print(" {}:".format(param_value.specmin))
            elif param_value.specmin == None and param_value.specmax != None:
                print("-999")

            if param_value.specmax != None:
                print(" {}:".format(param_value.specmax))
            elif param_value.specmin != None and param_value.specmax == None:
                print("999")

