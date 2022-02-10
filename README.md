# computer-networks-quizz-generator

IPv4 subnet generator and quizz generator with [XML Moodle output format support](https://docs.moodle.org/3x/fr/Question_cloze_à_réponses_intégrées)

Works with `python3`.

To use it
- edit and select whether you want to generate a quizz with hints (e.g. `wi_hints = True`), and the number of questions to generate (e.g. `max_questions = 100`)

Then 
  
    python3 generate-ipv4-subnets-and-quizz.py > xml-mooddle-quizz_100-train.xml # wi_hints = True 

Or

    python3 generate-ipv4-subnets-and-quizz.py > xml-mooddle-quizz_100-test.xml # wi_hints = False

