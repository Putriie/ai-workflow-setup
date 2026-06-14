"""
Fetch transcripts (no timestamps) for the 30 videos in
'Youtube URLs from Cursor's AI Agent.md'
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os
import re
import time

VIDEOS = [
    ("Samantha McKenna", "Show Me You Know Me: Mastering Personalization in Sales Outreach", "IfxqQWdMDYI"),
    ("Samantha McKenna", "Show Me You Know Me – Use Data To Personalize Your Outreach", "pzY4QlG-X5A"),
    ("Samantha McKenna", "Complete COLD EMAIL COURSE (Apollo Academy)", "H5zsGa9FeuI"),
    ("Josh Braun", "How to Overcome Prospect Resistance: 4T Cold Email Framework", "9cKZVyAQ3mY"),
    ("Josh Braun", "How to Create and Scale a Cold Email Prospecting Strategy", "vdtLIUmGkXs"),
    ("Josh Braun", "Let's Write a Good Cold Email", "lVUDHxrZJCY"),
    ("Kevin Dorsey", "Cold Calling Secrets REVEALED: CRO Kevin Dorsey's $100M+ Scripts", "MLo0V2mnHBw"),
    ("Kevin Dorsey", "The 10 Commandments of Daily Sales Success", "mKhcPYAEPYM"),
    ("Kevin Dorsey", "Why 90% of SDR Teams Fail (and How to Build the 10% That Don't)", "oVCB224tW6s"),
    ("Kyle Coleman", "Why Your Outbound Sucks (and How to Fix It)", "g9mejr_-odc"),
    ("Kyle Coleman", "Scaling Your Outbound Engine ft. Kyle Coleman", "Y7QLIHx1wpw"),
    ("Kyle Coleman", "AI in GTM: Effectiveness Over Efficiency", "GC3Wsg8gu00"),
    ("Jason Bay", "Outbound Prospecting Masterclass: Book Meetings in 2026", "dDM80maP1N0"),
    ("Jason Bay", "Cold Email Masterclass: Book Meetings in 2026", "JX1UNIJwcCY"),
    ("Jason Bay", "Live Cold Calls: How Many Meetings Can The #1 Sales Trainer Book?", "9WtOHUDgbIA"),
    ("Steli Efti", "Craft High-Performing Email Sequences (Webinar)", "XH2SHKREPDY"),
    ("Steli Efti", "How to Build a Solo SaaS Sales Machine (MicroConf 2015)", "8PuKwEfXZqc"),
    ("Steli Efti", "Sales Alchemy – Turn a Dry Pipeline into Golden Opportunities", "Sx6e-AIEeaY"),
    ("Alex Berman", "How to Cold Email Clients (Winning Cold Email Templates)", "hatrtJIncLc"),
    ("Alex Berman", "I Studied 1,000,000 Cold Emails, Here's What Works in 2025", "4qCXuIQO5T4"),
    ("Alex Berman", "The Insane Psychology Behind Cold Email", "8gi8tCb3Q4I"),
    ("Max Altschuler", "How To Hack Sales (Close More Deals, Easier)", "nfHBysGMenc"),
    ("Max Altschuler", "Everything Modern Sales and Outbound with Max Altschuler", "MtOB0W20Wjs"),
    ("Max Altschuler", "Early-Stage SaaS GTM with GTMfund's GP Max Altschuler", "9QQZd57NrdI"),
    ("Armand Farrokh", "[Playbook] Cold Email: Analyzing 85M+ Cold Emails (2025)", "yjOG_QOJgII"),
    ("Armand Farrokh", "Stop Failing at Cold Email in 2025… Teach Your Reps THIS!", "0KSenwLuFiE"),
    ("Armand Farrokh", "How to Write Cold Emails That Get Replies | Problem + Value Framework", "NLASslONNrU"),
    ("Morgan Ingram", "LinkedIn Blueprint – How SDRs Can Book More Meetings", "I-PmhgTQTik"),
    ("Morgan Ingram", "My LinkedIn Outbound Strategy That Books 25+ Meetings a Month", "nUe5IpnleRc"),
    ("Morgan Ingram", "LIVE Cold Outreach Sequence Tear-Downs", "C4WCOJa5Nwo"),
]


def fetch_transcript(api, video_id):
    langs = ["en", "en-US", "en-GB"]
    try:
        return api.fetch(video_id).to_raw_data()
    except Exception:
        pass

    transcript_list = api.list(video_id)
    for finder in [
        lambda: transcript_list.find_manually_created_transcript(langs),
        lambda: transcript_list.find_generated_transcript(langs),
        lambda: transcript_list.find_transcript(langs),
    ]:
        try:
            return finder().fetch().to_raw_data()
        except Exception:
            pass

    for t in transcript_list:
        try:
            return t.translate("en").fetch().to_raw_data()
        except Exception:
            continue

    raise NoTranscriptFound(video_id, langs, {})


def to_plain_text(segments):
    text = " ".join(seg["text"].strip() for seg in segments)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base, "transcripts")
    os.makedirs(out_dir, exist_ok=True)
    combined_path = os.path.join(base, "..", "youtube-transcripts.md")
    failed_path = os.path.join(base, "failed_videos.txt")

    sections = [
        "# Cold Outreach Research — YouTube Transcripts (No Timestamps)\n",
        "Transcripts fetched from the 30 videos selected in "
        "`Youtube URLs from Cursor's AI Agent.md`.\n",
    ]
    failed = []
    api = YouTubeTranscriptApi()

    for i, (expert, title, video_id) in enumerate(VIDEOS, 1):
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"{i:02d}/30 {expert[:18]:<18} ", end="", flush=True)
        try:
            segments = fetch_transcript(api, video_id)
            text = to_plain_text(segments)
            sections.append(f"## {i}. {expert} — {title}\n")
            sections.append(f"**URL:** {url}\n\n")
            sections.append(text + "\n\n---\n\n")
            fname = f"{i:02d}_{video_id}.txt"
            with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                f.write(f"EXPERT: {expert}\nTITLE: {title}\nURL: {url}\n\n{text}\n")
            print("OK")
        except Exception as e:
            print(f"FAIL: {e}")
            failed.append((expert, title, url, str(e)))
            sections.append(f"## {i}. {expert} — {title}\n")
            sections.append(f"**URL:** {url}\n\n")
            sections.append(f"*Transcript unavailable: {e}*\n\n---\n\n")
        time.sleep(0.4)

    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("".join(sections))

    if failed:
        with open(failed_path, "w", encoding="utf-8") as f:
            for expert, title, url, reason in failed:
                f.write(f"{expert} | {title}\n{url}\n{reason}\n\n")

    print(f"\nWrote {combined_path}")
    print(f"Success: {30 - len(failed)}/30 | Failed: {len(failed)}")


if __name__ == "__main__":
    main()

