# Hardcoded CSV header fields derived from sample-response.json (so the CSV columns are stable).
# The theory/practical subject names are taken from `sample-response.json` and used verbatim here.
CSV_FIELDNAMES = [
    "redg_no",
    "name",
    "father_name",
    "mother_name",
    "examYear",
    "semester",
    "exam_held",
    "cgpa",
    "sgpa",
    "fail_any",
]

# Theory subjects from sample-response.json
THEORY_SUBJECTS = [
    "ANALOG ELECTRONIC CIRCUITS",
    "DATA STRUCTURE & ALGORITHMS",
    "MATHEMATICS-III (DIFFERENTIAL CALCULUS)",
    "OBJECT ORIENTED PROGRAMMING USING C++",
    "TECHNICAL WRITING",
]

# Practical subjects from sample-response.json
PRACTICAL_SUBJECTS = [
    "Analog Electronics Circuits Laboratory",
    "DATA STRUCTURE & ALGORITHMS",
    "OBJECT ORIENTED PROGRAMMING USING C++",
    "Internship",
]