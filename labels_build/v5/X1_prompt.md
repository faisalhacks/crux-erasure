You will see a question that a small group of people discussed, followed by each person's written opinion. The opinions are numbered.

Task: find the two quotes, taken from two different people's opinions, that most strongly conflict with each other on the question.

Rules:
- Each quote must be copied exactly, character for character, from one opinion: one continuous passage (a phrase, a sentence or a few sentences). Do not change spelling, punctuation, capitalisation or spacing, and do not add, remove or join words.
- The two quotes must come from two different opinions.
- If no two opinions conflict, return the two quotes that are most different from each other and set "conflict_found" to false. Otherwise set "conflict_found" to true.

Question: {question}

Opinions:
{numbered_opinions}

Return JSON only, in this form:
{"opinion_a": <number of the opinion quote A comes from>, "quote_a": "<exact text>", "opinion_b": <number of the opinion quote B comes from>, "quote_b": "<exact text>", "conflict_found": true or false}
