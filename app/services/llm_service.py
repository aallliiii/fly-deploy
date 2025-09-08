from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config.settings import settings
from app.schemas.query_enchancements_schemas import QueryEnhancement, RerankedResults

class LLMService:
    def __init__(self):
        self.query_llm = ChatOpenAI(
            model=settings.LLM_MODEL_ENHANCER,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        self.reranker = ChatOpenAI(
            model=settings.LLM_MODEL_RERANKER,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
    
    async def enhance_query(self, user_query: str) -> QueryEnhancement:
        """Enhance user query for better retrieval"""
        
        enhancement_prompt = ChatPromptTemplate.from_template("""
        You are a search query enhancement expert. Given a user's search query, your task is to:
        1. Enhance the query for better semantic search results as well as you can
        2. Determine what type of items they're looking for (EVENT, PRODUCT, or both)
        3. Determine the audience (male/female/unisex) if mentioned otherwise set to None
        4. Extract any relevant keywords from the query to filter the results
        5. Extract time filters for events (future, past, today, this_week, this_month, next_week, next_month) if mentioned otherwise set to None
        6. Extract is_weekend for events if mentioned otherwise set to False
        
        
        User Query: {query}
        
        Guidelines:
        - Enhanced query should be more descriptive and include synonyms
        - If they mention clothing/fashion items etc, set search_type to "products"
        - If the query is simple like suggest me some events in this month or any thing like that then keep keywords to None
        - If they mention activities/entertainment/gatherings etc, set search_type to "events"  
        - If unclear or could be both, set to "both"
        - Extract audience (male/female/unisex) only if mentioned otherwise set to None
        - Be conservative with filters - only set them if clearly indicated
        - If it says i suggest me a dress for an event or something like that only set the search_type to "product" don't set it to both
        - The keywords should be added only if they are relevant to the query (for example if a query says suggest me some events for weekend then keyword should be weekend)
        - Don't add the words 'events' or 'products' in the keywords as they are already included in the search_type
        - The words like 'next week, week, today' etc should not be added as keyword filters because they are not in the content that is being embedded
        - Time filters should be extracted only for events:
          * "past" - for events that already happened
          * "future" - for upcoming events
          * "today" - for events happening today
          * "this_week" - for events happening this week
          * "this_month" - for events happening this month
          * "next_week" - for events happening next week
          * "next_month" - for events happening next month
        - Time-related words like 'next week', 'today', 'this weekend' should be mapped to appropriate time_filter, NOT added as keyword filters
        - If the query is for a weekend (Saturday or Sunday or weekend key word), set is_weekend to True otherwise set to False
        - Give alot of keywords using synonyms and related words


        Examples:
        - "summer dress for women" → search_type: "product", audience: "female", other_keyword_filters: "summer"
        - "weekend music events" → search_type: "events"
        - "i love rap music suggest me some events" → search_type: "event", other_keyword_filters: "rap, music, concerts, singing etc"
        - "upcoming concerts next month" → search_type: "event", time_filter: "next_month", other_keyword_filters: ["concerts"]
        - "events happening today" → search_type: "event", time_filter: "today"

        
        Return your response in the exact JSON format specified by the schema.

        Just for reference here is the sample text that is embedded in the VectorDB for both events and products so you can understand the format and extract keywords from user query:
        Product: This is a product named Tshirt which is Tshirt. It belongs to the T shirt category and is manufactured by the brand FLY. The product type is Unisex and comes in Black color. It is made from Cotton material and features a Casual style. This product is perfect for Casual wear occasions and offers a Regular fit. The design includes a Solid pattern and is ideal for the Summer season. It is targeted towards Unisex audience and includes special features such as Graphic/Logo Detail. The product is tagged with FLY, T shirt, Unisex, Solid.
        Event: This is an event called Live Music Event which is described as The best live music event for creatives. Come join us to discover the best up and coming artists. a night of music, creativity and vibes! last entry - 12am. The event starts on 05/09/2025 at 21:00 and ends on 06/09/2025 at 3:00. It takes place on a Friday during Working Days. The venue is located at Test Address in Manchester, b, United Kingdom with zip code M7 6LD. Tickets are priced at £20.0 and the event is organized by 24-30. This event falls under the Concerts category and has a status of 0. The genre is Concert and is designed for General Audience audience with age restriction of . Special features include Art Display, Live Music and it is an Indoor event. The dress code is and the event will be conducted in English language. This event is suitable for the Autumn season and is tagged with Concerts, Manchester , Concert, Art Display, Live Music.
        """)
        
        chain = enhancement_prompt | self.query_llm.with_structured_output(QueryEnhancement)
        result = await chain.ainvoke({"query": user_query})
        
        return result
    
    async def rerank_results(self, user_query: str, search_results: list, top_k: int = 7) -> RerankedResults:
        """Use LLM to rerank search results and return top K"""

        # Prepare results for LLM
        results_text = ""
        for i, result in enumerate(search_results, 1):
            content_preview = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
            results_text += f"""
    Result {i} (ID: {result['original_id']}, Type: {result['name_space']}):
    {content_preview}
    ---
    """
        
        reranking_prompt = ChatPromptTemplate.from_template("""
        You are a search result ranking expert. Given a user query and search results, rank the results by relevance.
        
        User Query: {query}
        
        Search Results:
        {results}
        
        Instructions:
        1. Analyze each result's relevance to the user query
        2. Consider semantic similarity, exact matches, and user intent
        3. Select the TOP {top_k} most relevant results
        4. Assign relevance scores from 1-10 (10 being most relevant)
        5. Provide brief explanations for why each result is relevant
        
        Focus on:
        - Direct relevance to user's search intent
        - Quality and completeness of information
        - Practical usefulness for the user
        
        Return relevant results in the specified JSON format.
        """)
        
        chain = reranking_prompt | self.reranker.with_structured_output(RerankedResults)
        
        reranked = await chain.ainvoke({
            "query": user_query,
            "results": results_text,
            "top_k": top_k
        })
        
        
        return reranked

llm_service = LLMService()