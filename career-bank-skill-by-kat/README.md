# Career Bank

A Claude skill that builds your Career Bank, a single source of truth for everything you have done at work, then uses it to gap-check job postings and write tailored resumes and cover letters.

Most resume help starts at the resume. This starts one layer earlier, because the reason almost nobody tailors their applications is that every attempt begins from a blank page.

## What it does

1. **Interviews you, once.** About 45 minutes, role by role. Works best in voice mode.
2. **Digs out numbers you think you do not have.** Seven angles on "I don't really have metrics," which is almost never true.
3. **Writes your bank to Notion.** Roles, metrics, systems you built, verbatim manager quotes, your through-line, your voice, and a positioning play per role type.
4. **Gap-checks a job posting** requirement by requirement, ending in a verdict: strong fit, stretch, reach, or skip.
5. **Asks what it does not know,** then writes the answers back into your bank. Every application makes the next one faster.
6. **Writes a tailored resume and cover letter** as `.docx`, ATS-safe, in your voice.
7. **Audits its own output for AI slop** before handing it to you.

## The walkthrough

Scaffolded by default. It stops at each stage, shows you the work, and asks before moving on. Ask for changes and it revises and asks again, as many rounds as you want. Say "express" to skip the gates when you are in a hurry.

## Install

1. [Download the skill zip](https://github.com/krettura/ai-skills-library/raw/main/downloads/career-bank-skill-by-kat.zip) (no GitHub account needed).
2. [Duplicate the Career Bank Notion template](https://military-sycamore-1d6.notion.site/Career-Portfolio-Accomplishments-Bank-Template-41d6fdcf51a481b1b785c263bbd500a5).
3. Connect Notion in Claude under Settings > Connectors, so it can read and write your bank. Optional, there is a file fallback.
4. Upload the zip under Skills.
5. Start a chat with "help me build my career bank."

Have your current resume handy, and your last performance review if you can find it. Verbatim manager quotes are the most persuasive material in any cover letter and you cannot reconstruct them from memory.

## What it will not do

It will not invent experience, inflate a title, or make up a number to close a gap. When something is genuinely missing it says so, then tells you whether that is worth a cover letter, worth learning, or worth skipping the job.

It will not hide keywords in white text or embed instructions aimed at AI screeners. People get caught and it is an instant rejection.

## Notes

- Paste the text of a job posting, not a link. LinkedIn, Greenhouse, Lever, and Workday all block automated reading.
- Resume format defaults to reverse-chronological, with hybrid for career changers and gaps. It asks during onboarding and stores your preference.
- The format, ATS, and authenticity standards follow current resume guidance and are worth re-checking once a year.
- The bank only stays useful if you feed it. Fifteen minutes a quarter.

Built by Kat Rettura.
