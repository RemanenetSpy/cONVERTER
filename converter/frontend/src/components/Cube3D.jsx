
import React from 'react';
import { FileText, Image, FileSpreadsheet, Music, Box, FileCode } from 'lucide-react';
import './Cube3D.css';

function Cube3D() {
    return (
        <div className="cube-container">
            <div className="cube">
                <div className="face front">
                    <FileText size={32} />
                    <span>DOC</span>
                </div>
                <div className="face back">
                    <Image size={32} />
                    <span>IMG</span>
                </div>
                <div className="face right">
                    <FileSpreadsheet size={32} />
                    <span>XLS</span>
                </div>
                <div className="face left">
                    <Music size={32} />
                    <span>MP3</span>
                </div>
                <div className="face top">
                    <Box size={32} />
                    <span>ZIP</span>
                </div>
                <div className="face bottom">
                    <FileCode size={32} />
                    <span>PDF</span>
                </div>
            </div>
        </div>
    );
}

export default Cube3D;
