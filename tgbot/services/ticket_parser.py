from typing import List

import xml.etree.ElementTree as ETree


def parse_ticket(file: str) -> List[dict]:
    """Parses text, answers and tips of tickets"""
    tree = ETree.parse(file)
    root = tree.getroot()
    ticket = list()
    
    for test in root.findall("Test"):
        question = test.attrib.get("Question")
        info = test.attrib.get("InfoFile")
        
        answers = dict()
        for ans in test.findall("Answer"):
            text = ans.text
            correct = int(ans.attrib.get("correct"))
            answers.update({text: correct})

        ticket.append({
            "text": question,
            "answers": answers,
            "info": info
        })

    return ticket
