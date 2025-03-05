-- Drop tables if they exist
DROP TABLE IF EXISTS apps;
DROP TABLE IF EXISTS pages;
DROP TABLE IF EXISTS admin;

-- Create apps table
CREATE TABLE apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    thumbnail_path TEXT NOT NULL,
    link TEXT NOT NULL,
    click_count INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pages table
CREATE TABLE pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admin table
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Insert default admin user (username: admin, password: admin123)
INSERT INTO admin (username, password_hash) VALUES 
('admin', 'pbkdf2:sha256:260000$7EoiVGkVqR2gxXD3$d44b8a64c9f17a74f6a7f6b38d7eef87d2dce7951f76c8af43c099f2b3c2f7c6');

-- Insert default content for pages
INSERT INTO pages (type, content) VALUES 
('about', '<h3 class="text-xl font-semibold mb-4">Welcome to Prabhat''s Workspace</h3>
<p class="mb-4">We are dedicated to providing high-quality educational resources and tools to help you advance in your tech career. Our carefully curated collection of applications covers various aspects of programming, web development, data science, and more.</p>
<p>Whether you''re a beginner taking your first steps into programming or an experienced developer looking to expand your skillset, we have resources that will help you achieve your goals.</p>'),
('contact', '<h3 class="text-xl font-semibold mb-4">Get in Touch</h3>
<p class="mb-4">We''d love to hear from you! Whether you have questions about our resources or want to suggest new content, feel free to reach out.</p>
<ul class="list-none space-y-2">
    <li><i class="fas fa-envelope mr-2"></i>Email: contact@prabhatsworkspace.com</li>
    <li><i class="fas fa-phone mr-2"></i>Phone: +1 (555) 123-4567</li>
    <li><i class="fas fa-map-marker-alt mr-2"></i>Location: Tech Hub, Innovation Street, Digital City</li>
</ul>');

-- Insert sample apps
INSERT INTO apps (name, thumbnail_path, link, click_count) VALUES 
('Python Learning App', 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=600&fit=crop', 'https://www.python.org/about/gettingstarted/', 2),
('Web Development Guide', 'https://images.unsplash.com/photo-1593720219276-0b1eacd0aef4?w=800&h=600&fit=crop', 'https://developer.mozilla.org/en-US/docs/Learn', 1),
('Data Science Tutorial', 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop', 'https://www.kaggle.com/learn', 0);
