from fastapi import APIRouter
import httpx
from bs4 import BeautifulSoup

router = APIRouter(prefix="/career", tags=["Career Guidance"])

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


async def scrape_careers24(keyword: str):
    url = f"https://www.careers24.com/jobs/?keywords={keyword}&location=South+Africa"
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("article.job-card")  # updated selector
            for card in cards[:10]:
                title_tag = card.select_one("h3.job-title")
                company_tag = card.select_one("div.job-company")
                location_tag = card.select_one("div.job-location")
                link_tag = card.select_one("a[href]")
                if title_tag and company_tag and location_tag and link_tag:
                    jobs.append({
                        "title": title_tag.get_text(strip=True),
                        "company": company_tag.get_text(strip=True),
                        "location": location_tag.get_text(strip=True),
                        "url": "https://www.careers24.com" + link_tag['href']
                    })
    except Exception as e:
        print(f"Careers24 scrape error: {e}")
    return jobs


async def scrape_jobmail(keyword: str):
    url = f"https://www.jobmail.co.za/jobs/search?keywords={keyword}"
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            listings = soup.select("div.job-card")  # updated selector
            for job in listings[:10]:
                title_tag = job.select_one("a.job-title")
                company_tag = job.select_one("div.company")
                location_tag = job.select_one("div.location")
                if title_tag and company_tag and location_tag:
                    jobs.append({
                        "title": title_tag.get_text(strip=True),
                        "company": company_tag.get_text(strip=True),
                        "location": location_tag.get_text(strip=True),
                        "url": "https://www.jobmail.co.za" + title_tag['href']
                    })
    except Exception as e:
        print(f"JobMail scrape error: {e}")
    return jobs


def generate_guidance(keyword: str, jobs: list):
    if not jobs:
        return f"Currently, there are no job postings for '{keyword}' in South Africa. Consider exploring related careers or broadening your search."
    else:
        return f"{len(jobs)} {keyword.title()} positions are currently available in South Africa. Consider applying to the listed jobs and gaining relevant experience."


@router.get("/guide/{keyword}")
async def career_guide(keyword: str):
    careers24_jobs = await scrape_careers24(keyword)
    jobmail_jobs = await scrape_jobmail(keyword)

    all_jobs = careers24_jobs + jobmail_jobs
    guidance = generate_guidance(keyword, all_jobs)

    return {
        "keyword": keyword,
        "guidance": guidance,
        "jobs": all_jobs
    }
