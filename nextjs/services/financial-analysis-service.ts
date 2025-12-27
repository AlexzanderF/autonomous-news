import { FinancialAnalysisArticle } from "@/dtos";

// Mock data for development - replace with actual API call when backend is ready
const mockArticles: FinancialAnalysisArticle[] = [
    {
        id: "1",
        slug: "us-treasury-yields-2024-outlook",
        title: "US Treasury Yields: What to Expect in 2024",
        content: `### Executive Summary

The bond market is signaling significant shifts as we head into 2024. After a tumultuous period of rate hikes, investors are now pricing in potential cuts by the Federal Reserve.

### Current Market Dynamics

Treasury yields have shown remarkable volatility throughout 2023. The 10-year yield touched 5% for the first time since 2007, sending shockwaves through equity markets and mortgage rates.

**Key Observations:**
- Short-term yields remain elevated due to Fed policy
- The yield curve inversion persists, historically signaling recession risk
- International demand for US treasuries has shown signs of weakening

### Technical Analysis

From a technical perspective, the 10-year yield is approaching critical support levels. A break below 4.25% could accelerate the move toward 4.0%, while resistance remains strong at 4.5%.

### Investment Implications

For portfolio allocation, we recommend:
1. Extending duration gradually as yields stabilize
2. Maintaining a barbell strategy with short and intermediate maturities
3. Considering TIPS for inflation protection

### Conclusion

The bond market outlook for 2024 remains constructive, with potential for capital appreciation as the Fed pivots toward a less hawkish stance. However, volatility is likely to persist as economic data continues to influence policy expectations.`,
        author: "MT Macro Threads Research",
        published_at: "2024-01-15T10:30:00Z",
        tags: ["Fixed Income", "Treasury", "Macro"],
        thumbnail_url: undefined,
    },
    {
        id: "2",
        slug: "sp500-q1-2024-outlook",
        title: "S&P 500 Q1 2024: Bull Market or Dead Cat Bounce?",
        content: `### Executive Summary

Equity markets have staged a remarkable recovery, but questions remain about sustainability...`,
        author: "MT Macro Threads Research",
        published_at: "2024-01-10T14:00:00Z",
        tags: ["Equities", "S&P 500", "Market Outlook"],
        thumbnail_url: undefined,
    },
    {
        id: "3",
        slug: "fed-rate-decision-january-2024",
        title: "Fed Rate Decision: What January FOMC Means for Markets",
        content: `### Executive Summary

The Federal Reserve's January meeting will set the tone for monetary policy in 2024...`,
        author: "MT Macro Threads Research",
        published_at: "2024-01-08T09:15:00Z",
        tags: ["Federal Reserve", "Interest Rates", "Monetary Policy"],
        thumbnail_url: undefined,
    },
    {
        id: "4",
        slug: "dollar-strength-emerging-markets",
        title: "Dollar Strength and Its Impact on Emerging Markets",
        content: `### Executive Summary

The US dollar's persistent strength continues to create headwinds for emerging market economies...`,
        author: "MT Macro Threads Research",
        published_at: "2024-01-05T11:45:00Z",
        tags: ["USD", "Emerging Markets", "FX"],
        thumbnail_url: undefined,
    },
];

/**
 * Fetch a financial analysis article by its slug
 */
export async function getFinancialAnalysisBySlug(
    slug: string
): Promise<FinancialAnalysisArticle | null> {
    // TODO: Replace with actual API call when backend is ready
    // const url = `${API_BASE_URL}/analysis/${slug}`;
    // const res = await fetch(url, { next: { revalidate: 60 } });

    // For now, return mock data
    const article = mockArticles.find((a) => a.slug === slug);
    return article || null;
}

/**
 * Fetch all financial analysis articles
 */
export async function getFinancialAnalysisArticles(): Promise<
    FinancialAnalysisArticle[]
> {
    // TODO: Replace with actual API call
    return mockArticles;
}
