"use strict";

const SITE_URL = "https://db-vol-1.github.io/portfolio/";
const resolvePath = (path) =>
    new URL(path.replace(/^\.\//, ""), SITE_URL).href;

async function loadBlogMap() {
    const response = await fetch(resolvePath("./blog/blog-map.json"));

    if (!response.ok) {
        throw new Error(`Failed to load blog-map.json: ${response.status}`);
    }

    return response.json();
}

const blogMapPromise = loadBlogMap();

async function loadBlogPosts() {
    const containers = document.querySelectorAll(".blog-post-container");
    if (!containers.length) return;

    const { posts } = await blogMapPromise;
    containers.forEach((container) => renderBlogPosts(container, posts));
}

async function loadProjects() {
    const containers = document.querySelectorAll(".projects-container");
    if (!containers.length) return;

    const { projects } = await blogMapPromise;
    containers.forEach((container) => renderProjects(container, projects));
}

function formatDate(dateString) {
    return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" })
        .format(new Date(`${dateString}T00:00:00`));
}

function renderProjects(container, projects) {
    const sortedProjects = [...projects].sort((a, b) => {
        const activeDifference = Number(b.ended === null) - Number(a.ended === null);
        if (activeDifference !== 0) {
            return activeDifference;
        }

        return b.started.localeCompare(a.started) ||
            (b.ended ?? "").localeCompare(a.ended ?? "");
    });

    for (const project of sortedProjects) {
        const card = document.createElement("article");
        card.className = "project-card";

        const image = document.createElement("img");
        image.src = resolvePath(project.image);
        image.alt = `${project.title} project`;

        const details = document.createElement("div");
        const title = document.createElement("h3");
        title.textContent = project.title;
        const description = document.createElement("p");
        description.textContent = project.description;
        const date = document.createElement("time");
        date.dateTime = project.started;
        date.textContent = `${formatDate(project.started)} - ${
            project.ended === null ? "Current" : formatDate(project.ended)
        }`;

        details.append(title, description, date);
        if (project.related_blog_posts?.length > 0) {
            const readMore = document.createElement("a");
            readMore.className = "read-more";
            readMore.href = resolvePath(project.related_blog_posts[0]);
            readMore.textContent = "Read more";
            details.append(readMore);
        }
        if (project.github_url) {
            const githubIcon = document.createElement("i");
            githubIcon.className = "fa-brands fa-github";
            githubIcon.setAttribute("aria-hidden", "true");

            const githubLink = document.createElement("a");
            githubLink.className = "read-more";
            githubLink.href = project.github_url;
            githubLink.target = "_blank";
            githubLink.rel = "noopener noreferrer";
            githubLink.append(githubIcon, document.createTextNode(" GitHub Repository"));
            details.append(githubLink);
        }
        card.append(image, details);
        container.append(card);
    }
}

function renderBlogPosts(container, posts) {
    const sortedPosts = [...posts].sort((a, b) => b.date.localeCompare(a.date));

    for (const post of sortedPosts) {
        const card = document.createElement("article");
        card.className = "blog-post-card";

        const image = document.createElement("img");
        image.src = resolvePath(post.image);
        image.alt = `${post.title} post`;

        const details = document.createElement("div");
        const title = document.createElement("h3");
        const link = document.createElement("a");
        link.href = resolvePath(post.url);
        link.textContent = post.title;
        title.append(link);

        const description = document.createElement("p");
        description.textContent = post.description;
        const date = document.createElement("time");
        date.dateTime = post.date;
        date.textContent = formatDate(post.date);

        details.append(title, description, date);
        card.append(image, details);
        container.append(card);
    }
}

loadBlogPosts().catch((error) => {
    console.error("Failed to load blog posts:", error);
});
loadProjects().catch((error) => {
    console.error("Failed to load projects:", error);
});
