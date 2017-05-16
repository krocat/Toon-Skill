from toonlib import Toon
from settings import username, password, applicationID

toon = Toon(username, password)

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            applicationID):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetStatus":
        return get_system_status()
    elif intent_name == "SetTemperature":
        return set_temperature(intent)
    elif intent_name == "SetProgram":
        return set_program(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Toon - Thanks"
    speech_output = "Thank you for using the Toon skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title,
                                                       speech_output,
                                                       None,
                                                       should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Toon by Eneco"
    speech_output = "Welcome to the Alexa Toon thermostat skill. " \
                    "You can ask me to turn Toon on or off, set the temperature or" \
                    "set a specific program "
    reprompt_text = "Please ask me to set the thermostat, " \
                    "for example set Toon to 20 degrees."
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_status():
    session_attributes = {}
    card_title = "Toon status"
    reprompt_text = ""
    speech_output = ""
    should_end_session = False
    
    try:
        temp = toon.temperature
        power = toon.power.value
        gas = round(float(toon.gas.daily_usage) / 1000, 2)

        if toon.thermostat_state is not None:
            state_name = str(toon.thermostat_state.name)
        else:
            set_point = float(toon.thermostat_info.current_set_point) / 100
            state_name = " a manual temperature of " + str(set_point) + " degrees celcius"

        speech_output = "Toon is set to " + state_name + ". The current room temperature is " \
                        + str(temp) + " degrees celcius. Power is at " + str(power) + " Watt." \
                        "Gas consumption for today is at " + str(gas) + " cubic meters."

    except:
        speech_output = "I was unable to get all the required metrics from Toon. Please try again later."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_temperature(intent):
    session_attributes = {}
    card_title = "Toon - set the room temperature"
    speech_output = "I'm not sure what temperature you wanted me to set. " \
                    "Please try again."
    reprompt_text = "I'm not sure what temperature you want me to set " \
                    "Try asking to set the temperature to 20 degrees, for instance."
    should_end_session = False

    if "temps" in intent["slots"]:
        temp = intent["slots"]["temps"]["value"]
        card_title = "Toon - setting the room temperature to " + temp.title()

        try:
            toon.thermostat = float(temp)
            speech_output = "Ok, temperature has been set to " + str(temp) + "."
        except:
            speech_output = "I'm sorry, I was unable to set the temperature."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_program(intent):
    session_attributes = {}
    card_title = "Toon - set thermostat program"
    speech_output = "I'm not sure what program you wanted me to set. " \
                    "Please try again."
    reprompt_text = "I'm not sure what program you want me to set " \
                    "Try asking to set Toon to Away, for instance."
    should_end_session = False

    if "program" in intent["slots"]:
        program_name = intent["slots"]["program"]["value"]

        if program_name.lower() in [state.name.lower() for state in toon.thermostat_states]:
            card_title = "Toon - setting the thermostat program " + program_name
 
            try:
                toon.thermostat_state = program_name
                speech_output = "Ok, program has been set to " + program_name + "."
            except:
                print(result)
                speech_output = "I'm sorry, I was unable to set the program."
        else:
            card_title = "Toon - could not find a program with name " + program_name

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
