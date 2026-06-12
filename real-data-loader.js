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
      // Update subject with real location/status
      if (data.subject) {
        for (const lang of ['ja', 'en']) {
          if (data.subject[lang]) {
            leaderData[personId].subject[lang].location = data.subject[lang].location;
            leaderData[personId].subject[lang].status = data.subject[lang].status;
          }
        }
      }
      
      // Update news with real news
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
