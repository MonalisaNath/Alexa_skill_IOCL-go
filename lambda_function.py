"""
 Copyright (C) 2020 Dabble Lab - All Rights Reserved
 You may use, distribute and modify this code under the
 terms and conditions defined in file 'LICENSE.txt', which
 is part of this source code package.
 
 For additional copyright information please
 visit : http://dabblelab.com/copyright
 """

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from boto3.dynamodb.conditions import Key, Attr

import logging
import json
import random
import os
import boto3
import requests
import string


# Defining the database region, table name and dynamodb persistence adapter
ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')
ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
#user_id=ask_sdk_dynamodb.partition_keygen.device_id_partition_keygen(request_envelope)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name,create_table=False,dynamodb_resource=ddb_resource)

# Initializing the logger and setting the level to "INFO"
# Read more about it here https://www.loggly.com/ultimate-guide/python-logging-basics/
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Intent Handlers

# This Handler is called when the skill is invoked by using only the invocation name(Ex. Alexa, open template ten)
class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        #persistent_attributes = handler_input.attributes_manager.persistent_attributes
        skill_name = language_prompts["SKILL_NAME"]
        
        try:
            # Fetch order name from the DB.
            item_name = persistent_attributes['item_name']
            speech_output = random.choice(language_prompts["REPEAT_USER_GREETING"]).format(item_name)
            reprompt = random.choice(language_prompts["REPEAT_USER_GREETING_REPROMPT"])
        except:
            speech_output = random.choice(language_prompts["FIRST_TIME_USER"]).format(skill_name)
            reprompt = random.choice(language_prompts["FIRST_TIME_USER_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class MyOrderIsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("MyOrderIsIntent")(handler_input) or is_request_type("LaunchRequest")(handler_input))
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        #name=handler_input.request_envelope.request.intent.slots["name"].value
        price=handler_input.request_envelope.request.intent.slots["price"].value
        item_name = handler_input.request_envelope.request.intent.slots["item"].value
        #persistent_attributes["name"] = name
        order_id=''.join(random.choices(string.ascii_lowercase,k=5))
        persistent_attributes["item_name"] = item_name
        persistent_attributes["price"] = price
        persistent_attributes["order_id"]=order_id
        table=boto3.resource('dynamodb').Table(ddb_table_name)
        
        # Write user's name to the DB.
        
            
        table.put_item(
            Item={
                #"id":handler_input.request_envelope.context.system.user.user_id,
                "id":order_id,
                "attributes":{
                  "dun":item_name,
                  "price":price
                }
               
            }
            )
            
        data = requests.get("http://api.open-notify.org/astros.json")
        data = json.loads(data.text)
        handler_input.attributes_manager.save_persistent_attributes()
        speech_output1 = random.choice(language_prompts["NAME_SAVED"]).format(price)
        reprompt = random.choice(language_prompts["NAME_SAVED_REPROMPT"])
        speech_output = random.choice(language_prompts["ASTRONAUTS_RESPONSE"]).format(len(data["people"]))
        i= 0
        while(i<len(data["people"])):
            if(i==0):
                name = data["people"][i]['name']
                speech_output = "{} Their names are: {}, ".format(speech_output,name)
                i+=1
            elif(i==len(data["people"])-1):
                name = data["people"][i]['name']
                speech_output = "{} and {}.".format(speech_output,name)
                i+=1
            else:
                name = data["people"][i]['name']
                speech_output = "{} {},".format(speech_output,name)
                i+=1
        
        
        return(
            handler_input.response_builder
                .speak(speech_output1)
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class WhatsMyOrderIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("WhatsMyOrderIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        try:
            # Read user's name from the DB.
            #item_name = persistent_attributes['item_name']
            price=persistent_attributes['price']
            speech_output = random.choice(language_prompts["TELL_NAME"]).format(price)
            reprompt = random.choice(language_prompts["TELL_NAME_REPROMPT"])
        except:
            speech_output = random.choice(language_prompts["NO_NAME"])
            reprompt = random.choice(language_prompts["NO_NAME_REPROMPT"])        
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class UpdateOrderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("UpdateOrderIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        price = handler_input.request_envelope.request.intent.slots["NewitemSlot"].value
        # Update user's name
        persistent_attributes["price"] = price
        handler_input.attributes_manager.save_persistent_attributes()
        #table=boto3.resource('dynamodb').Table(ddb_table_name)
        #table.put_item(
            #Item={
                #"id":handler_input.request_envelope.context.system.user.user_id,
                #"id":order_id,
                #"attributes":{
                  #"dun":item_name,
                  #"price":price
                #}
               
           # }
           # )
        
        speech_output = random.choice(language_prompts["NAME_UPDATED"]).format(price)
        reprompt = random.choice(language_prompts["NAME_UPDATED_REPROMPT"])
        
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class DeleteOrderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DeleteOrderIntent")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        # Delete all attributes from the DB
        handler_input.attributes_manager.delete_persistent_attributes()
        
        speech_output = random.choice(language_prompts["NAME_DELETED"])
        reprompt = random.choice(language_prompts["NAME_DELETED_REPROMPT"])
        
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )
class WhatavailableHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("Whatavailable")(handler_input)
    
    def handle(self,handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        
        handler_input.attributes_manager.delete_persistent_attributes()
        
        speech_output = random.choice(language_prompts["AVAILABLE_ITEM"])
        reprompt = random.choice(language_prompts["AVAILABLE_ITEM_REPROMPT"])
        
        return(
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        session_attributes = handler_input.attributes_manager.session_attributes
        
        repeat_speech_output = session_attributes["repeat_speech_output"]
        repeat_reprompt = session_attributes["repeat_reprompt"]
        
        speech_output = random.choice(language_prompts["REPEAT"]).format(repeat_speech_output)
        reprompt = random.choice(language_prompts["REPEAT_REPROMPT"]).format(repeat_reprompt)
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["CANCEL_STOP_RESPONSE"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# This handler handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Exception Handlers

# This exception handler handles syntax or routing errors. If you receive an error stating 
# the request handler is not found, you have not implemented a handler for the intent or 
# included it in the skill builder below
class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# Interceptors

# This interceptor logs each request sent from Alexa to our endpoint.
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

# This interceptor logs each response our endpoint sends back to Alexa.
class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))

# This interceptor is used for supporting different languages and locales. It detects the users locale,
# loads the corresponding language prompts and sends them as a request attribute object to the handler functions.
class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        
        try:
            with open("languages/"+str(locale)+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ str(locale[:2]) +".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts
    
# This interceptor fetches the speech_output and reprompt messages from the response and pass them as
# session attributes to be used by the repeat intent handler later on.
class RepeatInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes["repeat_speech_output"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        try:
            ession_attributes["repeat_reprompt"] = response.reprompt.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        except:
            session_attributes["repeat_reprompt"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")


 #Skill Builder
 #Define a skill builder instance and add all the request handlers,
# exception handlers and interceptors to it.

sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter)
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(MyOrderIsIntentHandler())
sb.add_request_handler(WhatsMyOrderIntentHandler())
sb.add_request_handler(UpdateOrderIntentHandler())
sb.add_request_handler(DeleteOrderIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())
sb.add_request_handler(WhatavailableHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_response_interceptor(RepeatInterceptor())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()