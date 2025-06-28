import React, { useState } from 'react';
import { X, ChevronLeft, ChevronRight, Image as ImageIcon, Video as VideoIcon } from 'lucide-react';

interface Attachment {
  id: string;
  file_url: string;
  file_name: string;
  file_type: 'image' | 'video';
  purpose: string;
  uploaded_at: string;
}

interface MediaGalleryProps {
  attachments: Attachment[];
  showTrigger?: boolean;
}

const MediaGallery: React.FC<MediaGalleryProps> = ({ attachments, showTrigger = true }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!attachments || attachments.length === 0) {
    return null;
  }

  const openGallery = (index: number = 0) => {
    setCurrentIndex(index);
    setIsOpen(true);
  };

  const closeGallery = () => {
    setIsOpen(false);
  };

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % attachments.length);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + attachments.length) % attachments.length);
  };

  const currentAttachment = attachments[currentIndex];

  const MediaTrigger = () => (
    <div className="flex items-center gap-2">
      {attachments.slice(0, 3).map((attachment, index) => (
        <button
          key={attachment.id}
          onClick={() => openGallery(index)}
          className="flex items-center justify-center w-12 h-12 bg-gray-100 hover:bg-gray-200 rounded-lg border transition-colors"
          title={`View ${attachment.file_name}`}
        >
          {attachment.file_type === 'image' ? (
            <ImageIcon className="w-6 h-6 text-gray-600" />
          ) : (
            <VideoIcon className="w-6 h-6 text-gray-600" />
          )}
        </button>
      ))}
      {attachments.length > 3 && (
        <button
          onClick={() => openGallery(3)}
          className="flex items-center justify-center w-12 h-12 bg-blue-100 hover:bg-blue-200 rounded-lg border transition-colors"
          title={`View all ${attachments.length} files`}
        >
          <span className="text-sm font-medium text-blue-600">+{attachments.length - 3}</span>
        </button>
      )}
    </div>
  );

  return (
    <>
      {showTrigger && <MediaTrigger />}

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90">
          <div className="relative max-w-4xl max-h-screen w-full h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 text-white">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-medium">
                  {currentAttachment.file_name}
                </h3>
                <span className="text-sm text-gray-300">
                  {currentIndex + 1} of {attachments.length}
                </span>
              </div>
              <button
                onClick={closeGallery}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Media Content */}
            <div className="flex-1 flex items-center justify-center p-4">
              {currentAttachment.file_type === 'image' ? (
                <img
                  src={currentAttachment.file_url}
                  alt={currentAttachment.file_name}
                  className="max-w-full max-h-full object-contain"
                />
              ) : (
                <video
                  src={currentAttachment.file_url}
                  controls
                  className="max-w-full max-h-full"
                >
                  Your browser does not support the video tag.
                </video>
              )}
            </div>

            {/* Navigation */}
            {attachments.length > 1 && (
              <>
                <button
                  onClick={prevImage}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 p-2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-lg transition-all"
                >
                  <ChevronLeft className="w-6 h-6" />
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 p-2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-lg transition-all"
                >
                  <ChevronRight className="w-6 h-6" />
                </button>
              </>
            )}

            {/* Thumbnails */}
            <div className="p-4 flex justify-center gap-2 overflow-x-auto">
              {attachments.map((attachment, index) => (
                <button
                  key={attachment.id}
                  onClick={() => setCurrentIndex(index)}
                  className={`flex-shrink-0 w-16 h-16 rounded-lg border-2 overflow-hidden transition-all ${
                    index === currentIndex
                      ? 'border-blue-400'
                      : 'border-gray-600 hover:border-gray-400'
                  }`}
                >
                  {attachment.file_type === 'image' ? (
                    <img
                      src={attachment.file_url}
                      alt={attachment.file_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-800 flex items-center justify-center">
                      <VideoIcon className="w-6 h-6 text-gray-400" />
                    </div>
                  )}
                </button>
              ))}
            </div>

            {/* File Info */}
            <div className="p-4 text-white text-sm">
              <div className="flex items-center gap-4">
                <span>Type: {currentAttachment.file_type.toUpperCase()}</span>
                <span>Purpose: {currentAttachment.purpose}</span>
                <span>
                  Uploaded: {new Date(currentAttachment.uploaded_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MediaGallery; 