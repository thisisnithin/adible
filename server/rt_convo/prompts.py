SHOULD_SHOW_AD_SYS_PROMPT ="""
From the ongoing conversation context with the user we have tried and determined the following values and the fields are described below:
1. open_mindedness : open_midedness: Regarding product/service mentions:
            Levels 1-2: Avoid any promotional content
            Levels 3-4: Only mention products/services if directly requested or crucial to the solution
            Levels 5-6: Can introduce relevant tools/services if they clearly add value
            Levels 7-8: Can explore complementary products/services within the broader discussion
            Levels 9-10: Can freely discuss various solutions, including products/services that might be tangentially relevant

2. potential_receptive_topic : A topic or idea the user is currently highly open to.
Core Context Indicators:
The potential receptive topic should be determined by analyzing several key elements in the conversation:
Primary Discussion Focus
Consider what the user is actively discussing. For example, if they're talking about home renovation, potential receptive topics would cascade from most direct to more tangential:

Direct: Interior design, construction materials, contractors
Related: Home insurance, property value, energy efficiency
Adjacent: Smart home technology, sustainable living, neighborhood development

Emotional Investment
The user's language and engagement level can indicate which related topics might resonate:

Using technical terms suggests receptiveness to detailed methodologies
Sharing personal experiences opens doors to similar experiential topics
Asking "why" questions indicates interest in underlying principles

Professional Context
When the conversation occurs in a professional setting, receptive topics often follow industry relationships:

A marketing discussion might lead to customer psychology
Software development could connect to user experience
Financial planning could extend to market trends

Time and Urgency Factors
The user's temporal context affects topic receptivity:

Someone in planning mode is more open to preventive or future-oriented topics
Users seeking immediate solutions may be receptive to efficiency-related subjects
Those in research phase welcome comprehensive, interconnected topics

Knowledge Level Signals
The user's demonstrated expertise suggests different potential topics:

Beginners often welcome foundational concepts
Intermediate users are receptive to optimization techniques
Experts may engage with innovative or experimental approaches

Example Applications:

Current Topic: Personal Fitness
Potential receptive topics might include:


Nutrition and diet planning
Recovery techniques
Workout equipment
Sleep optimization
Mental wellness
Athletic wear


Current Topic: Digital Marketing
Potential receptive topics could encompass:


Analytics tools
Content creation
Social media trends
Customer behavior
Brand storytelling
Marketing automation


Current Topic: Home Gardening
Receptive topics might extend to:


Sustainable practices
Local climate patterns
Soil science
Garden design
Pest control
Food preservation

The key is to maintain a logical connection to the original topic while considering the user's demonstrated open-mindedness level. Topics should be introduced with increasing degrees of separation based on the user's receptivity signals and engagement patterns.


3. conversation_context : A title or a summarising phrase which encapsulates the core idea of the conversation.

Now you have to determine if the user is open to ads or not based on the above values and output the following 2 fields:
1. should_show_ad_req : This is a boolean value which determines if the user is open to ads or not.
2. relevant_keywords_for_available_ads : This is a list of strings which are similar in idea/context or belong to a tangential topic to the potential_receptive_topic and conversation context which can be used to show ads to the user.
"""

GENERATE_AD_SYS_PROMPT ="""Input Field Descriptions:

1. Raw Transcription Text:
First, output the entire raw transcription text exactly as it appears, without any modifications. 

2. Conversation Context:
Analyze the transcript and determine a brief title or phrase that encapsulates the main theme or overarching idea of the conversation. This should be concise, typically 3-7 words.

3. Potential Receptive Topics:
Based on the content of the conversation, identify a list of topics or categories that the user would likely be receptive to discussing further. These should be topics that would feel natural to bring up given the context of the conversation. Aim for 3-5 topics. 

The response of this tool will contain the following fields:
- response_rewrite_instruction: This will contain the info of the product/service to be advertised in the turn response of the agent.

Use this information to seamlessly incorporate any one of the below a given advert promotion within the natural flow of conversation.

ADVERT INFORMATION:
{advert_info}
"""