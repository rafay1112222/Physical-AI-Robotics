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
    title: 'Physical AI & Humanoid Robotics Textbook Portal', // UPDATED TITLE
    tagline: 'Spec-Driven Technical Textbook and RAG Portal', // UPDATED TAGLINE
    favicon: 'img/favicon.ico',

    // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
    future: {
      v4: true, // Improve compatibility with the upcoming Docusaurus v4
    },

    // Set the production url of your site here
    url: 'https://physical-ai-robotics.example.com', // Placeholder URL
    baseUrl: '/',

    // GitHub pages deployment config.
    organizationName: 'PhysicalAI', // Changed for project context
    projectName: 'Physical-AI-Robotics', // Changed for project context

    onBrokenLinks: 'throw',

    // Even if you don't use internationalization, you can use this field to set
    // useful metadata like html lang. For example, if your site is Chinese, you
    // may want to replace "en" with "zh-Hans".
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
            // Please change this to your repo.
            // Remove this to remove the "edit this page" links.
            editUrl:
              'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          },
          blog: {
            showReadingTime: true,
            feedOptions: {
              type: ['rss', 'atom'],
              xslt: true,
            },
            // Please change this to your repo.
            // Remove this to remove the "edit this page" links.
            editUrl:
              'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
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
          title: 'Physical AI & Humanoid Robotics', // UPDATED NAV TITLE
          logo: {
            alt: 'Robot Logo',
            src: 'img/logo.svg',
          },
          items: [
            {
              type: 'docSidebar',
              sidebarId: 'textbookSidebar',
              position: 'left',
              label: 'Textbook Chapters', // UPDATED NAV LABEL
            },
            {to: '/blog', label: 'Blog', position: 'left'},
            {
              href: 'https://github.com/facebook/docusaurus', // Will update later
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
                  to: '/docs/chapter1_intro',
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
                  href: 'https://github.com/facebook/docusaurus',
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