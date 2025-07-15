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
    IHWP = "ihwp"
    HELICITY_FREQ = "helicity_freq"
    FLIP_STATE = "flip_state"
    HMS_MOMENTUM = "hms_momentum"
    SHMS_MOMENTUM = "shms_momentum"
    NPS_SWEEPER = "nps_sweeper"
    BLOCKLEVEL = "blocklevel"
    EDTM_RATE = "edtm_rate"
    PRESCALES = "prescales"
    RUN_FLAG = "run_flag"
    
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
    #create_condition_type(HallCconditions.NPS_ANGLE, ConditionType.FLOAT_FIELD, "NPS angle in deg")
    create_condition_type(HallCconditions.HWIEN, ConditionType.FLOAT_FIELD, "Horizontal Wien Angle")
    create_condition_type(HallCconditions.VWIEN, ConditionType.FLOAT_FIELD, "Vertical Wien Angle")
    create_condition_type(HallCconditions.IHWP, ConditionType.STRING_FIELD, "Insertable half-wave plate In/Out")
    create_condition_type(HallCconditions.HELICITY_FREQ, ConditionType.FLOAT_FIELD, "Helicity board frequency in Hz")
    create_condition_type(HallCconditions.FLIP_STATE, ConditionType.STRING_FIELD, "Spin flipper state")
    create_condition_type(HallCconditions.HMS_MOMENTUM, ConditionType.FLOAT_FIELD, "HMS momentum")
    create_condition_type(HallCconditions.SHMS_MOMENTUM, ConditionType.FLOAT_FIELD, "SHMS momentum")
    create_condition_type(HallCconditions.BLOCKLEVEL, ConditionType.INT_FIELD, "readout blocklevel")
    create_condition_type(HallCconditions.EDTM_RATE, ConditionType.INT_FIELD, "EDTM pulser rate in Hz")
    create_condition_type(HallCconditions.PRESCALES, ConditionType.JSON_FIELD, "")
    create_condition_type(HallCconditions.RUN_FLAG, ConditionType.STRING_FIELD, "Run flag for offline analysis (good, bad, suspicious, needcut)")
    #create_condition_type(HallCconditions., ConditionType.STRING_FIELD, "")
