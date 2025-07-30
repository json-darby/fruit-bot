from nltk.inference import ResolutionProver


'''
Provides utility functions for knowledge base integrity and logical checking,
acting as a form of error handling for logical consistency.
A separate utility, promoting modularity for the main bot logic.
'''

def kb_integrity(kb, read_expr):
    '''
    Checks the integrity of the knowledge base for contradictions.
    This function is essential for ensuring the logical consistency of the bot's knowledge.
    '''
    for fact in kb:
        if '->' in str(fact): # Handle logical rules
            try:
                neg_rule = read_expr(f"~({fact})")
                if ResolutionProver().prove(neg_rule, kb, verbose=False):
                    print(f"Error: The rule {fact} introduces contradictions in the knowledge base.")
                    exit()
            except Exception as e:
                print(f"Error while processing rule {fact}: {e}")
                exit()
        else: # Handle atomic facts
            try:
                neg_fact = read_expr(f"~{fact}")
                if neg_fact in kb or ResolutionProver().prove(neg_fact, kb, verbose=False):
                    print(f"Error: The knowledge base contains contradictions involving {fact}.")
                    exit()
            except Exception as e:
                print(f"Error while processing fact {fact}: {e}")
                exit()

def kb_check(expression, mode, knowledge_base, parse_expression):
    '''
    Performs logical checks against the knowledge base (^^^).
    It serves as a validation mechanism for new or existing logical statements.
    '''
    if isinstance(expression, str):
        expression = parse_expression(expression)
    try:
        if mode == "contradiction":
            neg_expression = parse_expression(f"~{expression}")
            if neg_expression in knowledge_base or ResolutionProver().prove(neg_expression, knowledge_base, verbose=False):
                return True
            return False
        elif mode == "resolution":
            if ResolutionProver().prove(expression, knowledge_base, verbose=False):
                return True
            neg_expression = parse_expression(f"~{expression}")
            if ResolutionProver().prove(neg_expression, knowledge_base, verbose=False):
                return False
            return "unknown error..."
    except:
        return "unknown error..."
