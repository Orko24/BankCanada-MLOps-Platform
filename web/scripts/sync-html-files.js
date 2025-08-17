#!/usr/bin/env node

/**
 * Post-build script to synchronize HTML files with the correct React bundle names
 * This script reads the asset-manifest.json and updates all HTML files to reference
 * the correct bundle files with their hashes.
 */

const fs = require('fs');
const path = require('path');

const BUILD_DIR = path.join(__dirname, '..', 'build');
const ASSET_MANIFEST_PATH = path.join(BUILD_DIR, 'asset-manifest.json');

function syncHtmlFiles() {
  console.log('🔄 Synchronizing HTML files with React bundle...');

  // Read the asset manifest to get the actual bundle filenames
  if (!fs.existsSync(ASSET_MANIFEST_PATH)) {
    console.error('❌ asset-manifest.json not found. Make sure to run this after npm run build.');
    process.exit(1);
  }

  const assetManifest = JSON.parse(fs.readFileSync(ASSET_MANIFEST_PATH, 'utf8'));
  const mainJs = assetManifest.files['main.js'];
  const mainCss = assetManifest.files['main.css'];

  if (!mainJs) {
    console.error('❌ Main JS bundle not found in asset manifest.');
    process.exit(1);
  }

  console.log(`📦 Found JS bundle: ${mainJs}`);
  console.log(`🎨 Found CSS bundle: ${mainCss}`);

  // Get all HTML files in the build directory
  const htmlFiles = fs.readdirSync(BUILD_DIR)
    .filter(file => file.endsWith('.html'))
    .filter(file => file !== 'index.html'); // Skip index.html as it's already processed by React

  console.log(`📄 Found ${htmlFiles.length} HTML files to sync:`, htmlFiles);

  // Update each HTML file
  htmlFiles.forEach(filename => {
    const filePath = path.join(BUILD_DIR, filename);
    let content = fs.readFileSync(filePath, 'utf8');

    // Replace the hardcoded bundle reference with the actual bundle
    const originalContent = content;
    
    // Replace JS bundle reference
    content = content.replace(
      /src=["']\.\/static\/js\/bundle\.js["']/g,
      `src="${mainJs}"`
    );

    // Add CSS bundle if not present and CSS exists
    if (mainCss && !content.includes(mainCss)) {
      // Insert CSS link before closing head tag
      const cssLink = `<link href="${mainCss}" rel="stylesheet">`;
      content = content.replace('</head>', `${cssLink}</head>`);
    }

    // Write back if changed
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ Updated ${filename}`);
    } else {
      console.log(`⚠️  No changes needed for ${filename}`);
    }
  });

  console.log('🎉 HTML file synchronization complete!');
}

// Run the script
if (require.main === module) {
  syncHtmlFiles();
}

module.exports = { syncHtmlFiles };
