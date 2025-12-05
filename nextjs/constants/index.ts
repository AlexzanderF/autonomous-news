import { NewsCategory, NewsItem, Sentiment } from "@/dtos";

export const MOCK_NEWS: NewsItem[] = [
  {
    id: '1',
    slug: 'quantum-entanglement-network-zurich',
    headline: 'Quantum Entanglement Network Goes Live in Zurich',
    summary: 'Researchers at ETH Zurich have successfully established the first metropolitan-scale quantum internet node, promising unhackable communication channels for financial institutions.',
    category: NewsCategory.TECH,
    sentiment: Sentiment.POSITIVE,
    sourceCount: 12,
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 mins ago
    imageUrl: 'https://picsum.photos/800/600?random=1',
    biasScore: 50,
    sentimentScore: 98
  },
  {
    id: '2',
    slug: 'global-carbon-capture-alliance-breakthrough',
    headline: 'Global Carbon Capture Alliance Announces Breakthrough',
    summary: 'A coalition of 40 nations has ratified the "Atmospheric Restoration Treaty", deploying autonomous drones for oceanic algae seeding.',
    category: NewsCategory.ENVIRONMENT,
    sentiment: Sentiment.POSITIVE,
    sourceCount: 45,
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(), // 2 hours ago
    imageUrl: 'https://picsum.photos/800/600?random=2',
    biasScore: 45,
    sentimentScore: 85
  },
  {
    id: '3',
    slug: 'lunar-helium-mining-rights-debate-un',
    headline: 'Lunar Helium-3 Mining Rights Spark Debate at UN',
    summary: 'Tensions rise as private corporations stake claims on prime lunar regolith zones. Security Council convenes emergency session regarding extraterrestrial resource sovereignty.',
    category: NewsCategory.SPACE,
    sentiment: Sentiment.CONTROVERSIAL,
    sourceCount: 28,
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 mins ago
    imageUrl: 'https://picsum.photos/800/600?random=3',
    biasScore: 60,
    sentimentScore: 92
  },
  {
    id: '4',
    slug: 'algorithmic-trading-flash-crash-zero-second',
    headline: 'Algorithmic Trading Flash Crash: The "Zero Second" Dip',
    summary: 'Major indices dipped 8% and recovered within 400 milliseconds due to conflicting AI trading bot strategies. Regulators are baffled.',
    category: NewsCategory.FINANCE,
    sentiment: Sentiment.NEGATIVE,
    sourceCount: 8,
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), // 5 mins ago
    imageUrl: 'https://picsum.photos/800/600?random=4',
    biasScore: 52,
    sentimentScore: 99
  },
  {
    id: '5',
    slug: 'neuralink-competitor-non-invasive-bci',
    headline: 'NeuraLink Competitor Unveils Non-Invasive BCI',
    summary: 'Startup "CortexFlow" demonstrates a headset capable of 90% accurate thought-to-text translation without surgical implants.',
    category: NewsCategory.TECH,
    sentiment: Sentiment.POSITIVE,
    sourceCount: 19,
    timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
    imageUrl: 'https://picsum.photos/800/600?random=5',
    biasScore: 48,
    sentimentScore: 70
  },
  {
    id: '6',
    slug: 'antarctic-ice-shelf-stabilizes',
    headline: 'Antarctic Ice Shelf Stabilizes Unexpectedly',
    summary: 'New satellite data suggests a temporary reversal in melt rates in the Western sector, potentially buying a decade for coastal cities.',
    category: NewsCategory.ENVIRONMENT,
    sentiment: Sentiment.NEUTRAL,
    sourceCount: 33,
    timestamp: new Date(Date.now() - 1000 * 60 * 360).toISOString(),
    imageUrl: 'https://picsum.photos/800/600?random=6',
    biasScore: 50,
    sentimentScore: 88
  }
];