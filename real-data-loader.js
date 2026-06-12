// AI Footprints - Real Data Loader
// This module loads real tracking data from JSON file

const REAL_DATA_URL = './data/page-data.json';

async function loadRealData() {
  try {
    const resp = await fetch(REAL_DATA_URL);
    if (!resp.ok) {
      console.warn('Failed to load real data, using fallback');
      return null;
    }
    return await resp.json();
  } catch (e) {
    console.warn('Error loading real data:', e);
    return null;
  }
}

function mergeRealData(leaderData, realData) {
  if (!realData) return leaderData;
  
  // Merge real data into LEADER_DATA
  for (const [personId, data] of Object.entries(realData)) {
    if (leaderData[personId]) {
      // Update subject with real location/status (skip if Unknown)
      if (data.subject) {
        for (const lang of ['ja', 'zh', 'en', 'ko']) {
          if (data.subject[lang]) {
            // Only overwrite location if real data has a valid location
            const realLoc = data.subject[lang].location;
            if (realLoc && realLoc !== 'Unknown') {
              leaderData[personId].subject[lang].location = realLoc;
            }
            // Only overwrite status if real data has a valid status
            const realStatus = data.subject[lang].status;
            if (realStatus && !realStatus.includes('Unknown')) {
              leaderData[personId].subject[lang].status = realStatus;
            }
          }
        }
      }
      
      // Update news with real news (only if we have news)
      if (data.news && data.news.length > 0) {
        leaderData[personId].news = data.news;
      }
      
      // Add tracking metadata
      leaderData[personId].realData = {
        trackedAt: data.tracked_at,
        newsCount: data.news_count,
        isLive: true
      };
    }
  }
  
  return leaderData;
}

// Export for use in main app
window.loadRealData = loadRealData;
window.mergeRealData = mergeRealData;
