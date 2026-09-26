from app.ai.gemini_client import gemini_client


class MultilingualSummarizer:

    async def summarize(
        self,
        text: str,
        language: str = "en",
        length: str = "medium",
    ) -> str:

        language_names = {
            "en": "English",
            "bn": "Bengali",
            "hi": "Hindi",
        }

        language_name = language_names.get(
            language,
            "English",
        )

        prompt = f"""
Summarize the following educational content
in {language_name}.

Summary length: {length}

Content:
{text}

Preserve important technical terms,
definitions, formulas, and examples.
"""

        return await gemini_client.generate(
            prompt
        )


multilingual_summarizer = (
    MultilingualSummarizer()
)