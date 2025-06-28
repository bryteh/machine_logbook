import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import Database from 'better-sqlite3';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|mp4|mov|avi/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image and video files are allowed'));
    }
  }
});

// Initialize SQLite database
const db = new Database('machine_logbook.db');

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS machines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    model_number TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS issues (
    id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    category TEXT NOT NULL,
    alarm_code TEXT,
    alarm_ocr_text TEXT,
    description TEXT NOT NULL,
    ai_summary TEXT,
    auto_title TEXT,
    is_runnable BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    downtime_minutes INTEGER,
    FOREIGN KEY (machine_id) REFERENCES machines (id)
  );

  CREATE TABLE IF NOT EXISTS remedies (
    id TEXT PRIMARY KEY,
    issue_id TEXT NOT NULL,
    description TEXT NOT NULL,
    ai_draft TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues (id)
  );

  CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY,
    issue_id TEXT,
    remedy_id TEXT,
    file_url TEXT NOT NULL,
    file_type TEXT NOT NULL,
    purpose TEXT DEFAULT 'Other',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues (id),
    FOREIGN KEY (remedy_id) REFERENCES remedies (id)
  );
`);

// Seed some sample machines
const existingMachines = db.prepare('SELECT COUNT(*) as count FROM machines').get();
if (existingMachines.count === 0) {
  const insertMachine = db.prepare('INSERT INTO machines (id, name, model_number) VALUES (?, ?, ?)');
  const machines = [
    { id: uuidv4(), name: 'CNC Mill #1', model_number: 'Haas VF-2' },
    { id: uuidv4(), name: 'CNC Mill #2', model_number: 'Haas VF-3' },
    { id: uuidv4(), name: 'CNC Lathe #1', model_number: 'Haas ST-20' },
    { id: uuidv4(), name: 'CNC Lathe #2', model_number: 'Haas ST-30' },
    { id: uuidv4(), name: 'EDM Machine', model_number: 'Mitsubishi EA12' },
  ];
  
  machines.forEach(machine => {
    insertMachine.run(machine.id, machine.name, machine.model_number);
  });
}

// Routes

// Get all machines
app.get('/api/machines', (req, res) => {
  try {
    const machines = db.prepare('SELECT * FROM machines ORDER BY name').all();
    res.json(machines);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get dashboard metrics
app.get('/api/dashboard/metrics', (req, res) => {
  try {
    const openIssues = db.prepare("SELECT COUNT(*) as count FROM issues WHERE status IN ('open', 'on_hold')").get();
    const resolvedIssues = db.prepare("SELECT COUNT(*) as count FROM issues WHERE status = 'resolved'").get();
    
    const avgDowntime = db.prepare(`
      SELECT AVG(downtime_minutes) as avg_downtime 
      FROM issues 
      WHERE status = 'resolved' AND downtime_minutes IS NOT NULL
    `).get();

    // Get issues trend for the last 30 days
    const trendData = db.prepare(`
      SELECT 
        DATE(created_at) as date,
        COUNT(*) as count
      FROM issues 
      WHERE created_at >= DATE('now', '-30 days')
      GROUP BY DATE(created_at)
      ORDER BY date
    `).all();

    res.json({
      openIssues: openIssues.count,
      resolvedIssues: resolvedIssues.count,
      avgDowntime: Math.round(avgDowntime.avg_downtime || 0),
      trendData
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all issues
app.get('/api/issues', (req, res) => {
  try {
    const { status, machine_id } = req.query;
    let query = `
      SELECT i.*, m.name as machine_name, m.model_number
      FROM issues i
      JOIN machines m ON i.machine_id = m.id
    `;
    const conditions = [];
    const params = [];

    if (status) {
      conditions.push('i.status = ?');
      params.push(status);
    }
    if (machine_id) {
      conditions.push('i.machine_id = ?');
      params.push(machine_id);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY i.created_at DESC';

    const issues = db.prepare(query).all(...params);
    res.json(issues);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get single issue with remedies and attachments
app.get('/api/issues/:id', (req, res) => {
  try {
    const { id } = req.params;
    
    const issue = db.prepare(`
      SELECT i.*, m.name as machine_name, m.model_number
      FROM issues i
      JOIN machines m ON i.machine_id = m.id
      WHERE i.id = ?
    `).get(id);

    if (!issue) {
      return res.status(404).json({ error: 'Issue not found' });
    }

    const remedies = db.prepare('SELECT * FROM remedies WHERE issue_id = ? ORDER BY created_at').all(id);
    const attachments = db.prepare('SELECT * FROM attachments WHERE issue_id = ? ORDER BY uploaded_at').all(id);

    res.json({
      ...issue,
      remedies,
      attachments
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create new issue
app.post('/api/issues', upload.array('media', 5), async (req, res) => {
  try {
    const issueId = uuidv4();
    const {
      machine_id,
      category,
      alarm_code,
      description,
      is_runnable
    } = req.body;

    // Generate AI title and summary (placeholder for now)
    const auto_title = `${category} Issue - ${new Date().toLocaleDateString()}`;
    const ai_summary = description.length > 100 ? description.substring(0, 100) + '...' : description;

    // Insert issue
    const insertIssue = db.prepare(`
      INSERT INTO issues (id, machine_id, category, alarm_code, description, auto_title, ai_summary, is_runnable)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    insertIssue.run(issueId, machine_id, category, alarm_code || null, description, auto_title, ai_summary, is_runnable === 'true' ? 1 : 0);

    // Handle file uploads
    if (req.files && req.files.length > 0) {
      const insertAttachment = db.prepare(`
        INSERT INTO attachments (id, issue_id, file_url, file_type, purpose)
        VALUES (?, ?, ?, ?, ?)
      `);

      req.files.forEach(file => {
        const fileType = file.mimetype.startsWith('image/') ? 'image' : 'video';
        const fileUrl = `/uploads/${file.filename}`;
        insertAttachment.run(uuidv4(), issueId, fileUrl, fileType, 'Other');
      });
    }

    // Get the created issue
    const newIssue = db.prepare(`
      SELECT i.*, m.name as machine_name, m.model_number
      FROM issues i
      JOIN machines m ON i.machine_id = m.id
      WHERE i.id = ?
    `).get(issueId);

    res.status(201).json(newIssue);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update issue status
app.put('/api/issues/:id/status', (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    
    let updateData = { status };
    let query = 'UPDATE issues SET status = ?';
    let params = [status];

    if (status === 'resolved') {
      updateData.resolved_at = new Date().toISOString();
      query += ', resolved_at = ?';
      params.push(updateData.resolved_at);

      // Calculate downtime
      const issue = db.prepare('SELECT created_at FROM issues WHERE id = ?').get(id);
      if (issue) {
        const createdAt = new Date(issue.created_at);
        const resolvedAt = new Date();
        const downtimeMinutes = Math.round((resolvedAt - createdAt) / (1000 * 60));
        
        updateData.downtime_minutes = downtimeMinutes;
        query += ', downtime_minutes = ?';
        params.push(downtimeMinutes);
      }
    }

    query += ' WHERE id = ?';
    params.push(id);

    const result = db.prepare(query).run(...params);
    
    if (result.changes === 0) {
      return res.status(404).json({ error: 'Issue not found' });
    }

    res.json({ message: 'Issue status updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add remedy to issue
app.post('/api/issues/:id/remedies', upload.array('media', 5), (req, res) => {
  try {
    const { id: issueId } = req.params;
    const { description } = req.body;
    const remedyId = uuidv4();

    // Insert remedy
    const insertRemedy = db.prepare(`
      INSERT INTO remedies (id, issue_id, description)
      VALUES (?, ?, ?)
    `);
    
    insertRemedy.run(remedyId, issueId, description);

    // Handle file uploads for remedy
    if (req.files && req.files.length > 0) {
      const insertAttachment = db.prepare(`
        INSERT INTO attachments (id, remedy_id, file_url, file_type, purpose)
        VALUES (?, ?, ?, ?, ?)
      `);

      req.files.forEach(file => {
        const fileType = file.mimetype.startsWith('image/') ? 'image' : 'video';
        const fileUrl = `/uploads/${file.filename}`;
        insertAttachment.run(uuidv4(), remedyId, fileUrl, fileType, 'Other');
      });
    }

    const newRemedy = db.prepare('SELECT * FROM remedies WHERE id = ?').get(remedyId);
    res.status(201).json(newRemedy);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// File upload endpoint
app.post('/api/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    res.json({
      filename: req.file.filename,
      originalname: req.file.originalname,
      size: req.file.size,
      url: `/uploads/${req.file.filename}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});