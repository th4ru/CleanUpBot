"""
Database models for system management
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SystemPC(db.Model):
    """Model for managed systems"""
    __tablename__ = 'system_pcs'
    
    id = db.Column(db.Integer, primary_key=True)
    pc_name = db.Column(db.String(120), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv4 or IPv6
    ssh_port = db.Column(db.Integer, default=22)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    private_key_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='offline')  # online, offline
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    cleanup_operations = db.relationship('CleanupOperation', backref='system', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pcName': self.pc_name,
            'ipAddress': self.ip_address,
            'sshPort': self.ssh_port,
            'username': self.username,
            'status': self.status,
            'lastSeen': self.last_seen.isoformat(),
            'createdAt': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<SystemPC {self.pc_name}>'


class SystemStatus(db.Model):
    """Model for storing system status snapshots"""
    __tablename__ = 'system_status'
    
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system_pcs.id'), nullable=False)
    uptime = db.Column(db.String(100))
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'systemId': self.system_id,
            'uptime': self.uptime,
            'cpuUsage': self.cpu_usage,
            'memoryUsage': self.memory_usage,
            'diskUsage': self.disk_usage,
            'recordedAt': self.recorded_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<SystemStatus {self.system_id}>'


class DiskSpace(db.Model):
    """Model for disk space information"""
    __tablename__ = 'disk_space'
    
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system_pcs.id'), nullable=False)
    mount_point = db.Column(db.String(255))
    total_space = db.Column(db.BigInteger)  # in bytes
    used_space = db.Column(db.BigInteger)   # in bytes
    free_space = db.Column(db.BigInteger)   # in bytes
    usage_percent = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'systemId': self.system_id,
            'mountPoint': self.mount_point,
            'totalSpace': self.total_space,
            'usedSpace': self.used_space,
            'freeSpace': self.free_space,
            'usagePercent': self.usage_percent,
            'recordedAt': self.recorded_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<DiskSpace {self.mount_point}>'


class CleanupOperation(db.Model):
    """Model for cleanup operation logs"""
    __tablename__ = 'cleanup_operations'
    
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('system_pcs.id'), nullable=False)
    cleanup_type = db.Column(db.String(50), nullable=False)  # cache, temp, logs, all
    status = db.Column(db.String(20), default='pending')  # pending, running, success, failed
    space_freed = db.Column(db.BigInteger, default=0)  # in bytes
    error_message = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'systemId': self.system_id,
            'cleanupType': self.cleanup_type,
            'status': self.status,
            'spaceFreed': self.space_freed,
            'errorMessage': self.error_message,
            'startedAt': self.started_at.isoformat(),
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def __repr__(self):
        return f'<CleanupOperation {self.cleanup_type}>'
