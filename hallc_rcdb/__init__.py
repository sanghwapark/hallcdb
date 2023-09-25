from rcdb.model import ConditionType

class HallCconditions(object):
    """
    Default conditions are defined in rcdb
    Additional condtions for Hall C DB are defined here
    """
    EXPERIMENT = "experiment"
    BEAM_ENERGY = "beam_energy"
    TARGET = "target"
    TARGET_ENC = "target_enc"
    BEAM_CURRENT = "beam_current"
    TOTAL_CHARGE = "total_charge"
    HMS_ANGLE = "hms_angle"
    SHMS_ANGLE = "shms_angle"
    NPS_ANGLE = "nps_angle"
    HWIEN = "hwien"
    VWIEN = "vwien"
    HELICITY_FREQ = "helicity_freq"
    FLIP_STATE = "flip_state"
    HMS_MOMENTUM = "hms_momentum"
    
def create_condition_types(db):
    """
    Checks if condition types listed in class exist in the database and create them if not
    :param db: RCDBProvider connected to database
    :type db: RCDBProvider

    :return: None
    """

    all_types_dict = {t.name: t for t in db.get_condition_types()}

    def create_condition_type(name, value_type, description=""):
        all_types_dict[name] if name in all_types_dict.keys() \
            else db.create_condition_type(name, value_type, description)

    # create condition type
    create_condition_type(HallCconditions.EXPERIMENT, ConditionType.STRING_FIELD, "Experiment name")
    create_condition_type(HallCconditions.BEAM_ENERGY, ConditionType.FLOAT_FIELD, "Beam energy in MeV")
    create_condition_type(HallCconditions.TARGET, ConditionType.STRING_FIELD, "Target type")
    create_condition_type(HallCconditions.BEAM_CURRENT, ConditionType.FLOAT_FIELD, "Average beam current in uA")
    create_condition_type(HallCconditions.TOTAL_CHARGE, ConditionType.FLOAT_FIELD, "")
    create_condition_type(HallCconditions.HMS_ANGLE, ConditionType.FLOAT_FIELD, "HMS angle in deg")
    create_condition_type(HallCconditions.SHMS_ANGLE, ConditionType.FLOAT_FIELD, "SHMS angle in deg")
    create_condition_type(HallCconditions.NPS_ANGLE, ConditionType.FLOAT_FIELD, "NPS angle in deg")
    #create_condition_type(HallCconditions., ConditionType.STRING_FIELD, "")
