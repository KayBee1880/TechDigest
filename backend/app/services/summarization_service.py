from app.clients.ai_provider import AIProviderClient, get_ai_provider_client
from app.extensions import db
from app.models import Article, Summary


class SummarizationService:
    def __init__(self, client: AIProviderClient | None = None):
        self.client = client or get_ai_provider_client()

    def summarize(self, article: Article) -> Summary:
        content = article.raw_content or article.title
        summary_text = self.client.summarize(content)

        summary = article.summary or Summary(article_id=article.id)
        summary.content = summary_text
        summary.provider = self.client.name
        summary.model_name = getattr(self.client, "model", self.client.name)

        article.summary_status = "completed"

        db.session.add(summary)
        db.session.commit()
        return summary
