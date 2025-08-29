const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;

//Handit.ai
const { trackNode } = require('@handit.ai/node');


class FileService {
  constructor(executionId) {
    this.assetsDir = path.join(__dirname, '../assets');
    this.ensureAssetsDirectory();
    this.executionId = executionId
  }

  /**
   * Ensure assets directory exists
   */
  async ensureAssetsDirectory() {
    try {
      await fs.access(this.assetsDir);
    } catch (error) {
      await fs.mkdir(this.assetsDir, { recursive: true });
    }
  }

  /**
   * Create multer instance that properly handles session_id
   */
  createMulterInstance() {
    return multer({
      storage: multer.diskStorage({
        destination: (req, file, cb) => {
          // We'll handle the session directory creation in the controller
          // For now, use a temporary location
          cb(null, this.assetsDir);
        },
        filename: (req, file, cb) => {
          // Keep original filename without modification
          cb(null, file.originalname);
        }
      }),
      limits: {
        fileSize: 50 * 1024 * 1024, // 50MB limit
        files: 10 // Maximum 10 files per request
      }
    });
  }

  /**
   * Move uploaded files to session directory
   * @param {Array} files - Array of uploaded files
   * @param {string} sessionId - Session identifier
   * @returns {Promise<Array>} Array of file information
   */
  async moveFilesToSession(files, sessionId) {
    const sessionDir = path.join(this.assetsDir, sessionId, 'files');

    // Ensure session directory exists
    await fs.mkdir(sessionDir, { recursive: true });

    const movedFiles = [];

    for (const file of files) {
      const sourcePath = file.path;
      const destinationPath = path.join(sessionDir, file.originalname);

      try {
        // Move file to session directory
        await fs.rename(sourcePath, destinationPath);

        movedFiles.push({
          originalName: file.originalname,
          filename: file.originalname,
          size: file.size,
          mimetype: file.mimetype,
          sessionId: sessionId,
          path: destinationPath,
          uploadedAt: new Date().toISOString()
        });
      } catch (error) {
        console.error(`Error moving file ${file.originalname}:`, error);
        // If move fails, try copy then delete
        try {
          await fs.copyFile(sourcePath, destinationPath);
          await fs.unlink(sourcePath);

          movedFiles.push({
            originalName: file.originalname,
            filename: file.originalname,
            size: file.size,
            mimetype: file.mimetype,
            sessionId: sessionId,
            path: destinationPath,
            uploadedAt: new Date().toISOString()
          });
        } catch (copyError) {
          console.error(`Failed to copy file ${file.originalname}:`, copyError);
          throw new Error(`Failed to process file ${file.originalname}`);
        }
      }
    }


         // Prepare tracking input with images and file info
     let trackingInput = {
       fileInfo: {
         totalFiles: files.length,
         sessionId: sessionId,
         destination: sessionDir,
         fileTypes: [...new Set(files.map(f => f.mimetype))],
         totalSize: files.reduce((sum, f) => sum + f.size, 0)
       },
       images: []  // Will contain base64 data for each image
     };

     // Add images to input if they are image files
     for (const file of movedFiles) {
       if (file.mimetype.startsWith('image/')) {
         try {
           const imageBuffer = await fs.readFile(file.path);
           const base64Image = imageBuffer.toString('base64');
           
           // Determine MIME type from file extension
           const fileExt = path.extname(file.originalname).toLowerCase();
           let mimeType;
           
           if (fileExt === '.jpg' || fileExt === '.jpeg') {
             mimeType = 'image/jpeg';
           } else if (fileExt === '.png') {
             mimeType = 'image/png';
           } else if (fileExt === '.gif') {
             mimeType = 'image/gif';
           } else if (fileExt === '.bmp') {
             mimeType = 'image/bmp';
           } else {
             mimeType = `image/${fileExt.substring(1)}`;
           }
           
           const dataUrl = `data:${mimeType};base64,${base64Image}`;
           trackingInput.images.push({
             filename: file.originalname,
             mimeType: mimeType,
             size: file.size,
             dataUrl: dataUrl
           });
           
           console.log(`📸 Added image to tracking input: ${file.originalname} (${mimeType})`);
         } catch (imageError) {
           console.error(`⚠️ Failed to read image ${file.originalname}:`, imageError.message);
         }
       }
     }

     // Prepare simple output
     let trackingOutput = {
       status: 'success',
       movedFiles: movedFiles.length,
       sessionId: sessionId,
       destination: sessionDir
     };

     await trackNode({
       input: trackingInput,
       output: trackingOutput,
       nodeName: 'ingestion',
       agentName: 'multi_currency',
       nodeType: 'tool',
       executionId: this.executionId
     });

    console.log(`📊 Handit.ai tracking completed for file ingestion`);


    return movedFiles;
  }

  /**
   * Get session files info
   * @param {string} sessionId - Session identifier
   * @returns {Object} Session files information
   */
  async getSessionFiles(sessionId) {
    try {
      const sessionDir = path.join(this.assetsDir, sessionId, 'files');
      const files = await fs.readdir(sessionDir);

      const fileDetails = await Promise.all(
        files.map(async (filename) => {
          const filePath = path.join(sessionDir, filename);
          const stats = await fs.stat(filePath);

          return {
            filename,
            path: filePath,
            size: stats.size,
            createdAt: stats.birthtime,
            modifiedAt: stats.mtime
          };
        })
      );

      return {
        sessionId,
        totalFiles: fileDetails.length,
        files: fileDetails
      };
    } catch (error) {
      throw new Error(`Failed to get session files: ${error.message}`);
    }
  }
}

module.exports = FileService;
