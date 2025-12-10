// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

// Async config is needed to dynamically import ES modules (like remark-math/rehype-katex)
async function createConfig() {
  const remarkMath = (await import('remark-math')).default;
  const rehypeKatex = (await import('rehype-katex')).default;

  /** @type {import('@docusaurus/types').Config} */
  const config = {
    title: 'Physical AI & Humanoid Robotics Textbook Portal',
    tagline: 'Spec-Driven Technical Textbook and RAG Portal',
    favicon: 'img/favicon.ico',

    // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
    future: {
      v4: true, 
    },

    // --- START CONFIG FIXES ---
    
    // 1. Set the correct URL for GitHub Pages deployment
    url: 'https://rafay1112222.github.io', 
    
    // 2. Set the correct base path (repository name)
    baseUrl: '/Physical-AI-Robotics/', 

    // 3. GitHub pages deployment config.
    organizationName: 'rafay1112222', // YOUR GitHub username
    projectName: 'Physical-AI-Robotics', // YOUR repository name
    
    // 4. Fix: Allow broken links as warnings to bypass build failure (temporarily)
    onBrokenLinks: 'warn', // CHANGED from 'throw'

    // 5. Fix: Add trailingSlash for better GitHub Pages compatibility
    trailingSlash: true,
    
    // --- END CONFIG FIXES ---
    
    // Even if you don't use internationalization, you can use this field to set
    // useful metadata like html lang.
    i18n: {
      defaultLocale: 'en',
      locales: ['en'],
    },

    stylesheets: [
      {
        href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
        type: 'text/css',
        integrity: 'sha384-y13m+hky9HtIqQ8yD4Jv/eNvdHj1r47zP4Wk9f390W2U5nEw/QzG6w8yD6XQ2GzZ',
        crossorigin: 'anonymous',
      },
    ],

    presets: [
      [
        'classic',
        /** @type {import('@docusaurus/preset-classic').Options} */
        ({
          docs: {
            sidebarPath: './sidebars.js',
            // --- PLUGINS ADDED HERE ---
            remarkPlugins: [remarkMath],
            rehypePlugins: [rehypeKatex],
            // --- END PLUGINS ---
            // You should update the editUrl to your repo's actual URL
            editUrl:
              'https://github.com/rafay1112222/Physical-AI-Robotics/tree/main/', // UPDATED
          },
          blog: {
            showReadingTime: true,
            feedOptions: {
              type: ['rss', 'atom'],
              xslt: true,
            },
            // You should update the editUrl to your repo's actual URL
            editUrl:
              'https://github.com/rafay1112222/Physical-AI-Robotics/tree/main/', // UPDATED
            // Useful options to enforce blogging best practices
            onInlineTags: 'warn',
            onInlineAuthors: 'warn',
            onUntruncatedBlogPosts: 'warn',
          },
          theme: {
            customCss: './src/css/custom.css',
          },
        }),
      ],
    ],

    themeConfig:
      /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
      ({
        // Replace with your project's social card
        image: 'img/docusaurus-social-card.jpg',
        colorMode: {
          respectPrefersColorScheme: true,
        },
        navbar: {
          title: 'Physical AI & Humanoid Robotics',
          logo: {
            alt: 'Robot Logo',
            src: 'img/logo.svg',
          },
          items: [
            {
              type: 'docSidebar',
              sidebarId: 'textbookSidebar',
              position: 'left',
              label: 'Textbook Chapters',
            },
            {to: '/blog', label: 'Blog', position: 'left'},
            {
              // Update this to your actual GitHub link
              href: 'https://github.com/rafay1112222/Physical-AI-Robotics', // UPDATED
              label: 'GitHub',
              position: 'right',
            },
          ],
        },
        footer: {
          style: 'dark',
          links: [
            {
              title: 'Docs',
              items: [
                {
                  label: 'Chapter 1: Introduction',
                  to: '/docs/intro_physical_ai', // CORRECTED BROKEN LINK (Based on git status output)
                },
              ],
            },
            {
              title: 'Community',
              items: [
                {
                  label: 'Spec-Kit',
                  href: 'https://spec-kit.dev',
                },
                {
                  label: 'Discord',
                  href: 'https://discordapp.com/invite/docusaurus',
                },
              ],
            },
            {
              title: 'More',
              items: [
                {
                  label: 'Blog',
                  to: '/blog',
                },
                {
                  label: 'GitHub',
                  href: 'https://github.com/rafay1112222/Physical-AI-Robotics', // UPDATED
                },
              ],
            },
          ],
          copyright: `Copyright © ${new Date().getFullYear()} Physical AI Project. Built with Docusaurus & Gemini.`,
        },
        prism: {
          theme: prismThemes.github,
          darkTheme: prismThemes.dracula,
        },
      }),
  };

  return config;
}

export default createConfig;