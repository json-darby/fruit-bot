#!/usr/bin/env python3

# NLTK inference setup
import tensorflow as tf
from fruit_prediction import predict_image
from nltk.sem import Expression
from misc import kb_check, kb_integrity
read_expr = Expression.fromstring


# Knowledgebase setup
import pandas
kb = []
data = pandas.read_csv('fruit_kb.csv', header=None)
for row in data[0]:
    kb.append(read_expr(row))
kb_integrity(kb, read_expr)


# AIML and chatbot setup
import aiml
import wikipedia
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="fruit.xml")

is_vectorisation_on = False ###

# print("Welcome! My name is Ferb, the friendly fruit bot. Ask me anything fruity!")

###

# SECTION 2 FUZZY AND MULTI VALUED LOGICS
# SECTION 3 ROBOFLOW

# check in last lab
def process_message(message):
    answer = kern.respond(message)
    if not answer:
        return "Hmm, I didn't quite catch that. Try rephrasing!"
    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            return params[1]
        elif cmd == 1:  # For Wikipedia...
            try:
                wSummary = wikipedia.summary(params[1], sentences=4, auto_suggest=True)
                return wSummary
            except:
                return "Sorry, I do not know that. Be more specific!"
        
##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####        
        elif cmd == 2:  # "Show me an image of *"
            fruit = params[1].strip()
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{fruit}"
            try:
                import requests
                res = requests.get(wiki_url)
                if res.status_code == 200:
                    data = res.json()
                    image = data.get("thumbnail", {}).get("source")
                    summary = data.get("extract", "")
                    if image:
                        return f"Here’s an image of {fruit}!\n{image}\n\n{summary}"
                    else:
                        return f"Sorry, I couldn't find an image of {fruit}, but here’s some info:\n{summary}"
                else:
                    return f"Couldn’t find anything for '{fruit}'."
            except Exception as e: # fix this later, fix this later...
                return f"Something went wrong trying to get that image {e}."
##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####        

        elif cmd == 31:  # "I know that * is *"
            object, subject = params[1].split(' is ')
            expr = read_expr(subject + '(' + object + ')')
            if kb_check(expr, "contradiction", kb, read_expr):
                return "Error: Adding {}({}) would contradict existing knowledge.".format(subject, object)
            else:
                kb.append(expr)
                return "OK, I will remember that {} is {}.".format(object, subject)

        elif cmd == 32:  # "Check that * is *"
            object, subject = params[1].split(' is ')
            object = object.replace(" ", "_").lower()
            subject = subject.replace(" ", "_").lower()
            expr = read_expr(subject + '(' + object + ')')
            resolution = kb_check(expr, "resolution", kb, read_expr)
            if resolution is True:
                return "Correct: {} is {}.".format(object, subject)
            elif resolution is False:
                return "Incorrect: {} is not {}.".format(object, subject)
            else:
                return "Sorry, I don't know if {} is {}.".format(object, subject)
        elif cmd == 99:
            if is_vectorisation_on:
                return vectorisation_response(params[1])
            else:
                return "I did not get that, please try again."
    else:
        return answer

def ferb_respond_mate(users_input, which_interface, image_pathway=None):
    IMAGE_SIZE = (256, 256)
    if image_pathway:
        model = tf.keras.models.load_model("fruit_model.h5")
        result = predict_image(model, IMAGE_SIZE, "fruit_categories.json", image_pathway)
        if which_interface == 1:
            print(f"Ferb predicts: {result}")
        elif which_interface == 2:
            return f"Ferb predicts: {result}"
        return

    if which_interface == 1:
        while True:
            inp = input("> ")
            if inp.lower() in ["bye", "exit", "quit"]:
                print("Goodbye! Have a splendid day!")
                break
            response = process_message(inp)
            print(response)
    elif which_interface == 2:
        return process_message(users_input)

# VECTORISATION VECTORISATION VECTORISATION

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

''' vectorisation '''
# copy of the aiml questions...
vector_model = {
    "WHAT IS A FRUIT": "A fruit is the mature ovary of a flowering plant, typically containing seeds.",
    "CAN FRUITS BE SEEDLESS": "Yes, some fruits, such as bananas and seedless grapes, are naturally seedless or have been bred to be seedless.",
    "WHAT IS THE LARGEST FRUIT": "The jackfruit is considered the largest fruit in the world.",
    "WHAT IS THE SMALLEST FRUIT": "One of the smallest fruits is the watermeal - a tiny aquatic plant fruit - although some berries are similarly diminutive.",
    "WHAT IS THE SWEETEST FRUIT": "Many would say mangoes or dates are among the sweetest, though it often depends on the variety.",
    "GIVE ME A RANDOM FACT ABOUT FRUIT": "Did you know there are over 2,000 varieties of apples grown worldwide?",
    "HOW MANY TYPES OF FRUIT ARE THERE": "There are thousands of fruit species around the world, each offering unique flavours and nutritional benefits.",
    "WHAT IS AN EXAMPLE OF A CITRUS FRUIT": "Oranges, lemons, limes and grapefruits are all examples of citrus fruits.",
    "WHICH FRUIT IS KNOWN FOR ITS HIGH VITAMIN C CONTENT": "Oranges are particularly renowned for their vitamin C content.",
    "WHAT FRUIT IS USED TO MAKE WINE": "Grapes are most commonly used to produce wine.",
    "WHAT IS A TROPICAL FRUIT": "Fruits such as pineapples, mangoes and papayas are classified as tropical fruits.",
    "WHICH FRUIT HAS A HARD EXTERIOR AND A SOFT INTERIOR": "Coconuts are well known for their hard outer shell and soft, edible interior.",
    "WHICH FRUIT IS KNOWN FOR ITS FUZZY SKIN": "The peach is celebrated for its soft, fuzzy skin.",
    "WHICH FRUIT IS DRIED TO MAKE RAISINS": "Grapes are dried to produce raisins.",
    "WHAT FRUIT IS SYNONYMOUS WITH JAMAICA": "Many associate the ackee fruit with Jamaica - it's even part of the national dish, ackee and saltfish!",
    "WHICH FRUIT HAS A SPIKY EXTERIOR": "The durian is famous for its spiky outer shell.",
    "WHICH FRUIT IS A STAPLE IN TROPICAL DIETS": "Bananas are a dietary staple in many tropical regions.",
    "WHICH FRUIT IS RICH IN POTASSIUM": "Bananas are well known for their high potassium content.",
    "WHAT IS THE MOST COMMON BERRY": "The strawberry is one of the most popular berries worldwide.",
    "WHAT ARE THE NUTRITIONAL BENEFITS OF FRUITS": "Fruits are an excellent source of vitamins, minerals, fibre and antioxidants.",
    "WHAT FRUIT IS USED TO MAKE GUACAMOLE": "The avocado is the key fruit in making guacamole.",
    "WHAT IS A STONE FRUIT": "Stone fruits, like peaches and plums, have a hard pit or stone inside.",
    "CAN FRUITS BE GROWN ORGANICALLY": "Yes, many fruits are grown organically without synthetic pesticides or fertilisers.",
    "WHICH FRUIT HAS THE HIGHEST WATER CONTENT": "Watermelons are renowned for their high water content.",
    "WHAT FRUIT IS POPULAR IN SMOOTHIES": "Bananas, berries and mangoes are popular choices for smoothies.",
    "WHICH FRUIT IS KNOWN FOR ITS TANGY TASTE": "Lemons are well known for their tangy, sour flavour.",
    "WHAT FRUIT IS OFTEN EATEN DRIED": "Fruits such as dates and apricots are commonly enjoyed in dried form.",
    "WHAT IS THE DIFFERENCE BETWEEN A FRUIT AND A VEGETABLE": "Botanically speaking, a fruit develops from a flower and contains seeds, whereas vegetables come from other parts of the plant.",
    "ARE FRUITS CONSIDERED HEALTHY": "Absolutely! Fruits are a vital part of a balanced and healthy diet!",
    "WHICH FRUITS HAVE A NAME CHANGE WHEN DRIED": (
        "Several fruits undergo name changes when dried:\n"
        "- Green grapes become raisins.\n"
        "- Green seedless grapes become sultanas.\n"
        "- Small, dark red/black Corinth grapes become currants.\n"
        "- Plums become prunes.\n"
        "- Jalapeño peppers become chipotles."
        ),
    "WHICH FRUIT IS THE LARGEST BERRY": "Surprisingly, the watermelon is considered the largest berry!",
    "WHICH FRUIT HAS THE HIGHEST AMOUNT OF VITAMIN C": "Despite oranges being popular, the Kakadu plum contains significantly more vitamin C!",
    "WHICH FRUIT HAS THE LOWEST GLYCEMIC INDEX": "Cherries are celebrated for their low glycaemic index, making them a brilliant choice!",
    "WHICH FRUIT IS HIGHEST IN FIBRE": "Raspberries are exceptionally high in dietary fibre, a fantastic option for a fibre boost!",
    "WHICH IS THE HOTTEST FRUIT": "The chilli pepper, although not often recognised as a fruit, is renowned for its fiery heat!"
}

vector_model_keys = list(vector_model.keys())
vectoriser = TfidfVectorizer().fit(vector_model_keys)
question_vectors = vectoriser.transform(vector_model_keys)

# cosine similarity...
def vectorisation_response(input_text):
    input_text = input_text.upper()
    input_vector = vectoriser.transform([input_text])
    similarities = cosine_similarity(input_vector, question_vectors).flatten()
    best_idx = similarities.argmax()

    if similarities[best_idx] > 0.5: # Threshold
        best_question = vector_model_keys[best_idx]
        return vector_model[best_question]
    else:
        return "I did not understand that. Could you please rephrase?"

# ferb_respond_mate("how many types of fruit are there?", 1)

''' First-Order Logic '''