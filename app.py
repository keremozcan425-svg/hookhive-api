"""
HookHive API - AI Content Hook Generator
Generates viral hooks, captions, and content ideas for social media platforms.
Built for RapidAPI marketplace monetization.
"""

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import random
import json
from datetime import datetime

app = FastAPI(
    title="HookHive - AI Content Hook Generator",
    description="""
    Generate viral hooks, captions, and content ideas optimized for TikTok, Instagram, YouTube, and Twitter/X.
    
    **Features:**
    - Platform-specific hook generation (TikTok, Instagram, YouTube, Twitter/X)
    - Multiple content styles (storytelling, controversial, educational, emotional, humorous)
    - Trending format detection
    - Caption + hashtag generation
    - Content calendar ideas
    
    **Use Cases:**
    - Content creators automating their ideation process
    - Marketing agencies scaling content production
    - Social media managers generating post ideas
    - App developers adding content suggestion features
    """,
    version="1.0.0",
    contact={"name": "HookHive API Support"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── DATA: Hook Templates & Patterns ────────────────────────────────────────

HOOK_TEMPLATES = {
    "storytelling": [
        "I {action} for {duration} and here's what happened...",
        "Nobody told me {topic} would change my life like this...",
        "The moment I realized {insight} about {topic}, everything changed.",
        "I spent {duration} studying {topic} so you don't have to.",
        "Here's the {topic} secret that {authority_figure} don't want you to know.",
        "My {topic} journey: from {bad_state} to {good_state} in {duration}.",
        "I asked {number} experts about {topic}. Their answers shocked me.",
        "What {duration} of {topic} taught me that school never did.",
        "The {topic} mistake I made that cost me {consequence}.",
        "Day {number} of {topic}: things are getting interesting...",
    ],
    "controversial": [
        "Unpopular opinion: {topic} is completely overrated.",
        "Stop doing {common_action}. Here's why it's ruining your {area}.",
        "Everyone is wrong about {topic}. Let me explain.",
        "{topic} is a scam and here's the proof.",
        "I'm going to say what nobody else will about {topic}.",
        "The {topic} industry doesn't want you to see this.",
        "Why I quit {topic} after {duration} (and what I do instead).",
        "Hot take: {common_belief} is completely false.",
        "{topic} 'experts' are lying to you. Here's the truth.",
        "This is why {topic} will be dead by {year}.",
    ],
    "educational": [
        "How to {action} in {duration} (step-by-step guide).",
        "{number} {topic} tips that actually work in {year}.",
        "The ultimate beginner's guide to {topic}.",
        "{topic} explained in {duration} — save this for later.",
        "Most people don't know this {topic} trick.",
        "Free {topic} masterclass (thread) 🧵",
        "How I {achievement} using only {method}.",
        "{topic} 101: Everything you need to know.",
        "The {number}-step {topic} formula that never fails.",
        "Watch this before you start {topic}.",
    ],
    "emotional": [
        "This {topic} story will make you rethink everything.",
        "I wasn't going to share this, but {topic} needs to be talked about.",
        "The {topic} moment that brought me to tears.",
        "If you're struggling with {topic}, this is for you.",
        "I wish someone told me this about {topic} sooner.",
        "To everyone who's been through {struggle}: you're not alone.",
        "This changed my perspective on {topic} forever.",
        "The most important {topic} lesson I've ever learned.",
        "Why {topic} matters more than you think.",
        "A letter to my younger self about {topic}.",
    ],
    "humorous": [
        "POV: You just discovered {topic} for the first time.",
        "Me explaining {topic} to my friends at 2am:",
        "When someone says {topic} is easy: 🤡",
        "{topic} expectations vs reality (it's not even close).",
        "Things {topic} people say vs what they actually mean.",
        "Tell me you're into {topic} without telling me you're into {topic}.",
        "The {number} stages of learning {topic}.",
        "Nobody: ... Me at 3am researching {topic}:",
        "If {topic} was a person, they'd be that friend who {funny_trait}.",
        "Rating {topic} trends from 'genius' to 'absolutely unhinged'.",
    ],
}

PLATFORM_FORMATS = {
    "tiktok": {
        "max_length": 150,
        "trending_formats": [
            "POV style", "Story time", "Get ready with me + topic",
            "Day in my life", "Things that just make sense",
            "Ranking/tier list", "Duet/stitch bait", "Tutorial speed-run",
            "Before and after", "Expectation vs reality",
        ],
        "best_practices": [
            "Hook viewers in first 1-3 seconds",
            "Use trending sounds when possible",
            "Keep text overlays short and punchy",
            "End with a question or CTA for comments",
            "Use pattern interrupts to maintain attention",
        ],
        "hashtag_style": "mix of niche and broad",
    },
    "instagram": {
        "max_length": 200,
        "trending_formats": [
            "Carousel (swipe) posts", "Reels with text overlay",
            "Behind the scenes", "Mini-documentary style",
            "Infographic carousels", "Quote cards",
            "Before/after transformations", "Photo dumps with story",
            "Collaboration posts", "Interactive polls/quizzes",
        ],
        "best_practices": [
            "First line is everything — make it scroll-stopping",
            "Use line breaks for readability",
            "Include a clear CTA (save, share, comment)",
            "Carousel posts get highest engagement",
            "Mix educational and entertaining content",
        ],
        "hashtag_style": "20-30 targeted hashtags",
    },
    "youtube": {
        "max_length": 100,
        "trending_formats": [
            "How-to tutorials", "Listicles (Top 10, Top 5)",
            "Challenge videos", "Reaction/commentary",
            "Documentary style", "Day in my life vlogs",
            "Comparison videos", "Myth busting",
            "Interview/podcast clips", "Shorts (60s max)",
        ],
        "best_practices": [
            "Title should create curiosity gap",
            "Use numbers and power words",
            "Thumbnail text should differ from title",
            "First 30 seconds determine retention",
            "Promise a clear outcome or revelation",
        ],
        "hashtag_style": "3-5 relevant tags",
    },
    "twitter": {
        "max_length": 280,
        "trending_formats": [
            "Thread (🧵)", "Hot take + thread",
            "Listicle tweet", "Quote tweet commentary",
            "Poll + insight", "One-liner wisdom",
            "Contrarian take", "Personal story arc",
            "Data/stat + insight", "Prediction tweet",
        ],
        "best_practices": [
            "First tweet must stand alone as compelling",
            "Use line breaks between ideas",
            "End threads with a summary + CTA",
            "Engage in replies within first hour",
            "Tweet during peak hours (8-10am, 12-1pm, 5-6pm)",
        ],
        "hashtag_style": "1-2 hashtags max",
    },
}

HASHTAG_DATABASE = {
    "fitness": ["#fitness", "#gym", "#workout", "#fitnessmotivation", "#gains", "#fitfam", "#bodybuilding", "#health", "#training", "#exercise"],
    "business": ["#business", "#entrepreneur", "#startup", "#money", "#success", "#hustle", "#motivation", "#marketing", "#growth", "#mindset"],
    "tech": ["#tech", "#technology", "#coding", "#programming", "#ai", "#innovation", "#software", "#developer", "#startup", "#digital"],
    "food": ["#food", "#cooking", "#recipe", "#foodie", "#homemade", "#chef", "#yummy", "#delicious", "#kitchen", "#mealprep"],
    "fashion": ["#fashion", "#style", "#outfit", "#ootd", "#streetwear", "#trendy", "#aesthetic", "#drip", "#clothing", "#lookbook"],
    "gaming": ["#gaming", "#gamer", "#videogames", "#twitch", "#esports", "#gameplay", "#streamer", "#pcgaming", "#consolegaming", "#gamingcommunity"],
    "education": ["#education", "#learning", "#studytips", "#knowledge", "#student", "#study", "#school", "#learnontiktok", "#edutok", "#tips"],
    "finance": ["#finance", "#investing", "#stocks", "#crypto", "#money", "#financialfreedom", "#trading", "#wealth", "#personalfinance", "#passiveincome"],
    "travel": ["#travel", "#wanderlust", "#vacation", "#explore", "#adventure", "#travelgram", "#tourism", "#destination", "#travelblogger", "#trip"],
    "music": ["#music", "#musician", "#producer", "#beats", "#song", "#hiphop", "#rap", "#singer", "#newmusic", "#musicproducer"],
    "beauty": ["#beauty", "#skincare", "#makeup", "#glowup", "#selfcare", "#routine", "#beautytips", "#skincareroutine", "#cosmetics", "#beautyhacks"],
    "sports": ["#sports", "#football", "#soccer", "#basketball", "#nfl", "#nba", "#athlete", "#training", "#sportsnews", "#gameday"],
    "motivation": ["#motivation", "#mindset", "#grind", "#discipline", "#goals", "#success", "#inspire", "#nevergiveup", "#selfimprovement", "#growth"],
    "lifestyle": ["#lifestyle", "#dailyroutine", "#aesthetic", "#vibes", "#life", "#dayinmylife", "#routine", "#productive", "#wellness", "#habits"],
    "comedy": ["#comedy", "#funny", "#humor", "#memes", "#lol", "#joke", "#viral", "#relatable", "#skit", "#entertainment"],
    "default": ["#viral", "#trending", "#fyp", "#foryou", "#explore", "#content", "#creator", "#socialmedia", "#contentcreator", "#growthtips"],
}

POWER_WORDS = [
    "secret", "proven", "ultimate", "shocking", "hidden",
    "powerful", "essential", "critical", "guaranteed", "exclusive",
    "insane", "game-changing", "revolutionary", "mind-blowing", "brutal",
    "underrated", "overlooked", "deadly", "unstoppable", "elite",
]

FILL_VALUES = {
    "duration": ["30 days", "6 months", "1 year", "2 weeks", "100 days", "3 months"],
    "number": ["3", "5", "7", "10", "12", "15", "21", "30", "50", "100"],
    "authority_figure": ["experts", "gurus", "professionals", "industry leaders", "top creators", "coaches"],
    "bad_state": ["zero", "nothing", "rock bottom", "complete beginner", "broke", "clueless"],
    "good_state": ["six figures", "mastery", "the top 1%", "financial freedom", "viral success", "expert level"],
    "consequence": ["everything", "thousands", "months of progress", "my reputation", "my confidence"],
    "common_action": ["this", "what everyone else does", "the old way", "following trends blindly"],
    "area": ["results", "growth", "progress", "success", "career", "life"],
    "common_belief": ["this popular advice", "the common approach", "what everyone recommends"],
    "year": ["2026", "2027", "2028"],
    "achievement": ["went viral", "grew to 100K followers", "made $10K", "built an audience", "quit my 9-5"],
    "method": ["free tools", "my phone", "organic content", "one simple strategy"],
    "struggle": ["burnout", "self-doubt", "failure", "rejection", "starting over"],
    "funny_trait": ["always shows up late but brings snacks", "gives unsolicited advice", "overshares at parties"],
    "action": ["tried this", "tested this method", "committed to this challenge", "went all in on this"],
    "insight": ["the real truth", "what actually matters", "the hidden pattern", "the real secret"],
}


# ─── MODELS ──────────────────────────────────────────────────────────────────

class HookRequest(BaseModel):
    topic: str = Field(..., description="The content topic (e.g., 'fitness', 'making money online', 'cooking')", min_length=1, max_length=200)
    platform: str = Field(default="tiktok", description="Target platform: tiktok, instagram, youtube, twitter")
    style: str = Field(default="mixed", description="Hook style: storytelling, controversial, educational, emotional, humorous, or mixed")
    count: int = Field(default=5, description="Number of hooks to generate (1-10)", ge=1, le=10)
    niche: Optional[str] = Field(default=None, description="Content niche for targeted hashtags (e.g., 'fitness', 'tech', 'finance')")
    include_hashtags: bool = Field(default=True, description="Whether to include hashtag suggestions")
    include_caption: bool = Field(default=True, description="Whether to include a full caption draft")

class HookResponse(BaseModel):
    hooks: list
    platform_tips: dict
    trending_formats: list
    generated_at: str

class CaptionRequest(BaseModel):
    topic: str = Field(..., description="The content topic", min_length=1, max_length=200)
    platform: str = Field(default="instagram", description="Target platform")
    tone: str = Field(default="engaging", description="Tone: engaging, professional, casual, inspirational, witty")
    include_cta: bool = Field(default=True, description="Include a call-to-action")
    include_hashtags: bool = Field(default=True, description="Include hashtag suggestions")

class CalendarRequest(BaseModel):
    niche: str = Field(..., description="Content niche", min_length=1, max_length=100)
    platform: str = Field(default="tiktok", description="Target platform")
    days: int = Field(default=7, description="Number of days to plan (1-30)", ge=1, le=30)


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def fill_template(template: str, topic: str) -> str:
    """Fill a hook template with the topic and random contextual values."""
    result = template.replace("{topic}", topic)
    for key, values in FILL_VALUES.items():
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, random.choice(values))
    return result


def generate_hooks(topic: str, style: str, count: int, platform: str) -> list:
    """Generate hooks based on topic, style, and platform."""
    hooks = []

    if style == "mixed":
        styles = list(HOOK_TEMPLATES.keys())
    else:
        styles = [style] if style in HOOK_TEMPLATES else list(HOOK_TEMPLATES.keys())

    attempts = 0
    while len(hooks) < count and attempts < count * 5:
        chosen_style = random.choice(styles)
        template = random.choice(HOOK_TEMPLATES[chosen_style])
        hook_text = fill_template(template, topic)

        if hook_text not in [h["text"] for h in hooks]:
            # Add a power word variant sometimes
            power_word = random.choice(POWER_WORDS)
            hooks.append({
                "text": hook_text,
                "style": chosen_style,
                "power_word_variant": hook_text.replace(topic, f"{power_word} {topic}") if random.random() > 0.5 else None,
                "estimated_engagement": random.choice(["🔥 High", "⚡ Medium-High", "✅ Medium"]),
            })
        attempts += 1

    return hooks[:count]


def get_hashtags(niche: Optional[str], platform: str, count: int = 15) -> list:
    """Get relevant hashtags for the niche and platform."""
    if niche and niche.lower() in HASHTAG_DATABASE:
        tags = HASHTAG_DATABASE[niche.lower()].copy()
    else:
        tags = HASHTAG_DATABASE["default"].copy()

    # Add some cross-niche popular tags
    extra = HASHTAG_DATABASE["default"].copy()
    tags.extend([t for t in extra if t not in tags])

    random.shuffle(tags)

    if platform == "twitter":
        return tags[:3]
    elif platform == "youtube":
        return tags[:5]
    else:
        return tags[:count]


def generate_caption(topic: str, platform: str, tone: str, include_cta: bool) -> str:
    """Generate a full caption for the given topic and platform."""
    openers = {
        "engaging": [
            f"This is the {topic} content you've been waiting for.",
            f"Real talk about {topic} — no fluff, just facts.",
            f"If you're serious about {topic}, save this post.",
        ],
        "professional": [
            f"Key insights on {topic} that every professional should know.",
            f"A data-driven look at {topic} and what it means for you.",
            f"Breaking down the fundamentals of {topic}.",
        ],
        "casual": [
            f"So I've been getting into {topic} lately and wow.",
            f"Ok but why is nobody talking about {topic} like this?",
            f"Just some thoughts on {topic} — take what resonates.",
        ],
        "inspirational": [
            f"Your {topic} journey starts with one step.",
            f"The {topic} transformation nobody expected.",
            f"What {topic} has taught me about life.",
        ],
        "witty": [
            f"If {topic} was easy, everyone would do it. Oh wait.",
            f"{topic}: because apparently I needed another obsession.",
            f"My relationship with {topic} is complicated. Here's why.",
        ],
    }

    opener = random.choice(openers.get(tone, openers["engaging"]))

    body_lines = [
        f"\n\nHere's what most people get wrong about {topic}:\n",
        f"→ They focus on the wrong things",
        f"→ They give up too early",
        f"→ They don't have the right strategy\n",
        f"The truth? {topic.capitalize()} comes down to consistency and the right approach.",
    ]

    cta_options = [
        "\n\n💬 Drop a comment if you agree!",
        "\n\n🔖 Save this for later — you'll need it.",
        "\n\n↗️ Share this with someone who needs to hear it.",
        "\n\n👇 What's your experience with this? Let me know below.",
        "\n\n🔔 Follow for more content like this.",
    ]

    caption = opener + "".join(body_lines)
    if include_cta:
        caption += random.choice(cta_options)

    return caption


def generate_content_calendar(niche: str, platform: str, days: int) -> list:
    """Generate a content calendar with daily post ideas."""
    content_types = [
        {"type": "Educational", "description": f"Teach something valuable about {niche}"},
        {"type": "Behind the Scenes", "description": f"Show your {niche} process or daily routine"},
        {"type": "Story/Personal", "description": f"Share a personal {niche} experience or lesson"},
        {"type": "Trending", "description": f"Put your {niche} spin on a current trend"},
        {"type": "Engagement Bait", "description": f"Ask a polarizing question about {niche}"},
        {"type": "Tips/Listicle", "description": f"Share {random.randint(3,10)} quick {niche} tips"},
        {"type": "Myth Busting", "description": f"Debunk a common {niche} myth"},
        {"type": "Transformation", "description": f"Show before/after or progress in {niche}"},
        {"type": "Collaboration", "description": f"Feature or react to another {niche} creator"},
        {"type": "Controversial Take", "description": f"Share an unpopular {niche} opinion"},
    ]

    calendar = []
    today = datetime.now()

    for i in range(days):
        day_content = random.choice(content_types)
        style = random.choice(list(HOOK_TEMPLATES.keys()))
        template = random.choice(HOOK_TEMPLATES[style])
        hook = fill_template(template, niche)

        calendar.append({
            "day": i + 1,
            "content_type": day_content["type"],
            "description": day_content["description"],
            "suggested_hook": hook,
            "best_posting_time": random.choice([
                "8:00 AM", "10:00 AM", "12:00 PM",
                "2:00 PM", "5:00 PM", "7:00 PM", "9:00 PM"
            ]),
            "format": random.choice(PLATFORM_FORMATS.get(platform, PLATFORM_FORMATS["tiktok"])["trending_formats"]),
        })

    return calendar


# ─── API ENDPOINTS ───────────────────────────────────────────────────────────

@app.get("/")
def root():
    """API health check and info."""
    return {
        "api": "HookHive - AI Content Hook Generator",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/generate-hooks": "POST - Generate viral content hooks",
            "/generate-caption": "POST - Generate full captions with hashtags",
            "/content-calendar": "POST - Generate a multi-day content plan",
            "/trending-formats": "GET - Get trending content formats by platform",
            "/hashtags": "GET - Get hashtag suggestions by niche",
        },
    }


@app.post("/generate-hooks", response_model=HookResponse)
def generate_hooks_endpoint(request: HookRequest):
    """
    Generate viral content hooks for any topic and platform.
    
    Returns optimized hooks with style tags, engagement estimates,
    and platform-specific tips.
    """
    platform = request.platform.lower()
    if platform not in PLATFORM_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Choose from: {', '.join(PLATFORM_FORMATS.keys())}",
        )

    style = request.style.lower()
    valid_styles = list(HOOK_TEMPLATES.keys()) + ["mixed"]
    if style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Choose from: {', '.join(valid_styles)}",
        )

    hooks = generate_hooks(request.topic, style, request.count, platform)

    # Add hashtags and captions if requested
    for hook in hooks:
        if request.include_hashtags:
            hook["hashtags"] = get_hashtags(request.niche or request.topic, platform)
        if request.include_caption:
            hook["caption_draft"] = generate_caption(
                request.topic, platform, "engaging", True
            )

    platform_data = PLATFORM_FORMATS[platform]

    return HookResponse(
        hooks=hooks,
        platform_tips={
            "best_practices": platform_data["best_practices"],
            "max_caption_length": platform_data["max_length"],
            "hashtag_strategy": platform_data["hashtag_style"],
        },
        trending_formats=random.sample(
            platform_data["trending_formats"],
            min(5, len(platform_data["trending_formats"])),
        ),
        generated_at=datetime.now().isoformat(),
    )


@app.post("/generate-caption")
def generate_caption_endpoint(request: CaptionRequest):
    """
    Generate a full platform-optimized caption with optional CTA and hashtags.
    """
    platform = request.platform.lower()
    if platform not in PLATFORM_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Choose from: {', '.join(PLATFORM_FORMATS.keys())}",
        )

    caption = generate_caption(
        request.topic, platform, request.tone.lower(), request.include_cta
    )

    result = {
        "caption": caption,
        "platform": platform,
        "tone": request.tone,
        "character_count": len(caption),
    }

    if request.include_hashtags:
        result["hashtags"] = get_hashtags(request.topic, platform)
        result["hashtag_string"] = " ".join(result["hashtags"])

    return result


@app.post("/content-calendar")
def content_calendar_endpoint(request: CalendarRequest):
    """
    Generate a multi-day content calendar with daily post ideas,
    hooks, formats, and optimal posting times.
    """
    platform = request.platform.lower()
    if platform not in PLATFORM_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Choose from: {', '.join(PLATFORM_FORMATS.keys())}",
        )

    calendar = generate_content_calendar(request.niche, platform, request.days)

    return {
        "niche": request.niche,
        "platform": platform,
        "total_days": request.days,
        "calendar": calendar,
        "general_tips": PLATFORM_FORMATS[platform]["best_practices"],
    }


@app.get("/trending-formats")
def trending_formats_endpoint(
    platform: str = Query(default="tiktok", description="Platform: tiktok, instagram, youtube, twitter"),
):
    """Get currently trending content formats for a specific platform."""
    platform = platform.lower()
    if platform not in PLATFORM_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Choose from: {', '.join(PLATFORM_FORMATS.keys())}",
        )

    data = PLATFORM_FORMATS[platform]
    return {
        "platform": platform,
        "trending_formats": data["trending_formats"],
        "best_practices": data["best_practices"],
        "hashtag_strategy": data["hashtag_style"],
    }


@app.get("/hashtags")
def hashtags_endpoint(
    niche: str = Query(..., description="Content niche (e.g., 'fitness', 'tech', 'finance')"),
    platform: str = Query(default="instagram", description="Target platform"),
    count: int = Query(default=15, description="Number of hashtags (1-30)", ge=1, le=30),
):
    """Get curated hashtag suggestions for any niche and platform."""
    tags = get_hashtags(niche, platform.lower(), count)
    return {
        "niche": niche,
        "platform": platform,
        "hashtags": tags,
        "hashtag_string": " ".join(tags),
        "count": len(tags),
    }
