# util function for testing your code, DO NOT modify!!!

import pickle, gzip, os, random
import os

from logic import *


def checkFormula(name, predForm, preconditionForm=None):
    filename = os.path.join("models", name + ".pklz")
    objects, targetModels = pickle.load(gzip.open(filename))

    # If preconditionion exists, change the formula to
    preconditionPredForm = (
        And(preconditionForm, predForm) if preconditionForm else predForm
    )
    predModels = performModelChecking(
        [preconditionPredForm], findAll=True, objects=objects
    )
    ok = True

    def hashkey(model):
        return tuple(sorted(str(atom) for atom in model))

    targetModelSet = set(hashkey(model) for model in targetModels)
    predModelSet = set(hashkey(model) for model in predModels)
    for model in targetModels:
        if hashkey(model) not in predModelSet:
            print(
                "Your formula (%s) says the following model is FALSE, but it should be TRUE:"
                % predForm
            )
            ok = False
            printModel(model)
            return
    for model in predModels:
        if hashkey(model) not in targetModelSet:
            print(
                "Your formula (%s) says the following model is TRUE, but it should be FALSE:"
                % predForm
            )
            ok = False
            printModel(model)
            return

    print(f"You matched the {len(targetModels)} models")
    print(f"Example model: {rstr(random.choice(targetModels))}")
    return True
