from epics import caget

def main():
    epics_list = ["HALLC:p", "HALL_C_TARGET", "ibcm1"]
    for epics_name in epics_list:
        try:
            value = caget(epics_name)
            print(epics_name, value)
        except Exception as ex:
            print(str(ex))

if __name__=="__main__":
    main()
