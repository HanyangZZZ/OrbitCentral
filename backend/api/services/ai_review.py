"""
AI Review service — GPT-4.1 powered conversational review assistant.

Uses OpenAI function calling to let the AI add/remove tags on the business
as it learns about the user's experience through natural conversation.
"""
import json
import logging
import os

import openai

from ..models import Business, Tag

logger = logging.getLogger('api')

MODEL = 'gpt-4.1'

# ── Tool definitions for OpenAI function calling ──────────────────────────────

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'add_tag',
            'description': (
                'Add a descriptive tag to the business based on what the user '
                'confirmed about their experience.  Only add tags the user '
                'explicitly validated (e.g. "yes the patio was great" → outdoor-seating).'
            ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'tag_name': {
                        'type': 'string',
                        'description': (
                            'Lowercase hyphenated tag name (1-2 words). '
                            'Examples: cozy, pet-friendly, wifi, outdoor-seating, '
                            'live-music, vegan, craft-beer, late-night'
                        ),
                    },
                    'reason': {
                        'type': 'string',
                        'description': 'Brief reason based on user response.',
                    },
                },
                'required': ['tag_name', 'reason'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'remove_tag',
            'description': (
                'Remove a tag from the business because the user indicated it '
                'is inaccurate.  For example if the business is tagged "wifi" '
                'but the user says there is no wifi.'
            ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'tag_name': {
                        'type': 'string',
                        'description': 'The tag name to remove.',
                    },
                    'reason': {
                        'type': 'string',
                        'description': 'Brief reason based on user response.',
                    },
                },
                'required': ['tag_name', 'reason'],
            },
        },
    },
]


def _get_openai_client() -> openai.OpenAI:
    return openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def _build_system_prompt(business: Business, rating: int) -> str:
    """Build the system prompt with business context."""

    # Gather business info
    tags = list(business.tags.values_list('name', flat=True))
    category_name = str(business.category) if business.category else 'Unknown'

    # Build attribute summary for context
    attrs = []
    bool_fields = [
        ('dine_in', 'dine-in'), ('takeout', 'takeout'), ('delivery', 'delivery'),
        ('reservable', 'reservable'), ('serves_beer', 'beer'), ('serves_wine', 'wine'),
        ('serves_breakfast', 'breakfast'), ('serves_lunch', 'lunch'),
        ('serves_dinner', 'dinner'), ('serves_brunch', 'brunch'),
        ('outdoor_seating', 'outdoor seating'), ('live_music', 'live music'),
        ('good_for_children', 'kid-friendly'), ('good_for_groups', 'group-friendly'),
        ('allows_dogs', 'dog-friendly'), ('restroom', 'restroom'),
    ]
    for field, label in bool_fields:
        val = getattr(business, field, None)
        if val is True:
            attrs.append(label)

    attrs_str = ', '.join(attrs) if attrs else 'none listed'
    tags_str = ', '.join(tags) if tags else 'none yet'

    price_map = {0: 'Free', 1: 'Inexpensive', 2: 'Moderate', 3: 'Expensive', 4: 'Very Expensive'}
    price_str = price_map.get(business.price_level, 'unknown')

    return f"""You are a friendly, casual review-writing assistant for Orbit, a local business discovery app.

== BUSINESS CONTEXT ==
Name: {business.name}
Category: {category_name}
Address: {business.address or 'N/A'}
Price level: {price_str}
Google rating: {business.google_rating}/5 ({business.user_rating_count} Google reviews)
Current tags: [{tags_str}]
Known attributes: {attrs_str}
Description: {business.description or 'No description available'}
User's rating: {rating}/5

== YOUR ROLE ==
You're chatting with someone who just visited {business.name} and gave it {rating} stars.
Have a natural, friendly conversation to understand their experience. You're like a friend
asking "so how was it?" — NOT a survey bot.

== CONVERSATION GUIDELINES ==
1. Start with a warm opener based on their rating. If 4-5 stars, be enthusiastic.
   If 1-2, be empathetic. If 3, be curious.
2. Ask about 2-4 things naturally, one at a time. Don't list questions.
   Good topics based on the business type:
   - The overall vibe/atmosphere
   - Specific things they tried (food, service, products)
   - Whether the existing tags are accurate (casually, like "I see people say it's cozy — did you get that vibe?")
   - Staff friendliness, wait times, value for money
   - Anything unique or surprising about the visit
3. Keep each message SHORT (2-3 sentences max). This is chat, not an essay.
4. Be flexible — follow THEIR lead. If they mention something interesting, dig into that.
5. After gathering enough info (usually 3-5 exchanges), naturally wrap up and say you'll
   write up a review for them.

== TAG TOOLS ==
You have tools to ADD or REMOVE tags on this business:
- If the user CONFIRMS a tag is accurate (e.g. "yeah the patio is nice") — no need to add, it's already there.
- If the user reveals something NOT in current tags (e.g. they mention live music and it's not tagged) → use add_tag.
- If a tag seems WRONG based on user's experience (e.g. tagged "wifi" but user says no wifi) → use remove_tag.
- Only use tools when you have CLEAR evidence from the user. Don't guess.
- Keep tag names short, lowercase, hyphenated: "outdoor-seating", "craft-beer", "pet-friendly"

== IMPORTANT ==
- Do NOT write the review yet. Just chat. The review generation is a separate step.
- Do NOT ask all questions at once. One topic per message.
- Do NOT be robotic. No numbered lists of questions. Be human.
- Match the user's energy. Short reply? Keep yours short. Detailed reply? Engage deeper.
- Use the business context to make your questions specific (mention the business name, its food type, etc.)"""


def start_chat(business: Business, rating: int) -> list[dict]:
    """
    Start a new AI review chat session.
    Returns the initial messages list including the AI's first message.
    """
    client = _get_openai_client()
    system_prompt = _build_system_prompt(business, rating)

    messages = [{'role': 'system', 'content': system_prompt}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        temperature=0.8,
        max_tokens=300,
    )

    assistant_msg = response.choices[0].message
    content = assistant_msg.content or ''
    logger.info('AI review start_chat response length=%d', len(content))
    messages.append({'role': 'assistant', 'content': content})
    return messages


def continue_chat(
    messages: list[dict],
    user_message: str,
    business: Business,
    rating: int,
) -> tuple[list[dict], str, list[str], list[str]]:
    """
    Continue an AI review chat with the user's next message.

    Returns:
        (updated_messages, assistant_reply, tags_added, tags_removed)
    """
    client = _get_openai_client()

    # Rebuild system prompt in case it was stripped for storage
    if not messages or messages[0].get('role') != 'system':
        system_prompt = _build_system_prompt(business, rating)
        messages.insert(0, {'role': 'system', 'content': system_prompt})

    messages.append({'role': 'user', 'content': user_message})

    tags_added = []
    tags_removed = []

    # Loop to handle multiple tool calls in sequence
    max_rounds = 5  # safety limit
    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0.8,
            max_tokens=300,
        )

        choice = response.choices[0]

        if choice.finish_reason == 'tool_calls' or choice.message.tool_calls:
            # AI wants to call tool(s) before responding
            tool_msg = choice.message
            # Store the assistant's tool call message
            messages.append({
                'role': 'assistant',
                'content': tool_msg.content or '',
                'tool_calls': [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments,
                        },
                    }
                    for tc in tool_msg.tool_calls
                ],
            })

            # Process each tool call
            for tc in tool_msg.tool_calls:
                fn_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {}

                tag_name = args.get('tag_name', '').lower().strip()
                reason = args.get('reason', '')

                if fn_name == 'add_tag' and tag_name:
                    tags_added.append(tag_name)
                    result = f'Tag "{tag_name}" queued for addition. Reason: {reason}'
                    logger.info('AI review chat: add_tag("%s") — %s', tag_name, reason)
                elif fn_name == 'remove_tag' and tag_name:
                    tags_removed.append(tag_name)
                    result = f'Tag "{tag_name}" queued for removal. Reason: {reason}'
                    logger.info('AI review chat: remove_tag("%s") — %s', tag_name, reason)
                else:
                    result = 'Unknown tool or missing tag_name.'

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tc.id,
                    'content': result,
                })

            # Continue the loop so the AI generates a user-facing response after tool calls
            continue
        else:
            # Normal text response — we're done
            assistant_reply = choice.message.content or ''
            messages.append({'role': 'assistant', 'content': assistant_reply})
            return messages, assistant_reply, tags_added, tags_removed

    # Fallback if we hit the safety limit
    assistant_reply = messages[-1].get('content', '') if messages else ''
    return messages, assistant_reply, tags_added, tags_removed


def generate_review_description(
    messages: list[dict],
    business: Business,
    rating: int,
) -> str:
    """
    After the conversation, generate a polished review description from the
    collected information.
    """
    client = _get_openai_client()

    # Build a summary prompt — we don't need tools for this step
    generation_prompt = f"""Based on our conversation above, write a review for {business.name}.

Requirements:
- Write in FIRST PERSON as the reviewer (use "I", "my", "we")
- Keep it natural and genuine — like a real person wrote it on Google/Yelp
- Include specific details from what they told you (food items, atmosphere, staff, etc.)
- Match the tone to their {rating}-star rating
- Length: 2-5 sentences. Concise but descriptive.
- Do NOT include the star rating in the text
- Do NOT include phrases like "I'd give it X stars" or "Overall rating:"
- Do NOT be overly flowery or use marketing language
- Just output the review text, nothing else — no quotes, no prefix, no "Here's your review:"
"""

    # Filter out system messages and tool messages for the generation call
    # but keep the conversation flow
    gen_messages = []
    for m in messages:
        if m.get('role') == 'system':
            continue
        if m.get('role') == 'tool':
            continue
        # Strip tool_calls from assistant messages for clean context
        clean = {'role': m['role'], 'content': m.get('content', '')}
        if clean['content']:
            gen_messages.append(clean)

    gen_messages.append({'role': 'user', 'content': generation_prompt})

    # Use a separate system prompt for review generation
    system = (
        'You are a review writer. Write a genuine, personal review based on '
        'the conversation. Output ONLY the review text — no preamble, no quotes.'
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'system', 'content': system}] + gen_messages,
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def apply_tag_changes(business: Business, tags_to_add: list[str], tags_to_remove: list[str]):
    """
    Apply accumulated tag changes to the business.
    Creates new Tag objects for genuinely new tags.
    """
    if tags_to_add:
        for tag_name in tags_to_add:
            tag_name = tag_name.lower().strip()
            if len(tag_name) < 2 or len(tag_name) > 100:
                continue
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            business.tags.add(tag)
        logger.info('Applied %d tag additions to %s', len(tags_to_add), business.name)

    if tags_to_remove:
        for tag_name in tags_to_remove:
            tag_name = tag_name.lower().strip()
            try:
                tag = Tag.objects.get(name=tag_name)
                business.tags.remove(tag)
            except Tag.DoesNotExist:
                pass  # tag doesn't exist, nothing to remove
        logger.info('Applied %d tag removals from %s', len(tags_to_remove), business.name)
