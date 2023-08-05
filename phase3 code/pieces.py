from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Piece(QLabel):
    # Shared flyweight pixmap object
    pixmap_cache = {}

    def __init__(self, parent, score_label, pixmap_path, initial_position, weight, board, pieces, shape, colour, player):
        super().__init__(parent)
        
        # Check if the pixmap is already in the cache
        if pixmap_path in Piece.pixmap_cache:
            self.pixmap = Piece.pixmap_cache[pixmap_path]
        else:
            # Load the pixmap and store it in the cache
            self.pixmap = QPixmap(pixmap_path)
            Piece.pixmap_cache[pixmap_path] = self.pixmap
        
        # Rest of the code...
        self.setPixmap(self.pixmap)
        self.setAlignment(Qt.AlignCenter)
        self.Layout = board
        self.colour = colour
        self.pieces = pieces
        self.shape = shape
        self.dragging = False
        self.offset = QPoint()
        self.score_label = score_label
        self.initial_position = initial_position
        self.onboard = False
        self.movable = False #So that by default pieces are not movable
        self.weight = weight
        self.player = player
        self.board = board

        self.last_confirmed_position = self.initial_position
        self.new_position = None

        self.move(self.initial_position)
        self.setScaledContents(True)
        self.set_size_by_percentage(1)

        self.set_color_overlay(Qt.gray)
        # Create a mask from the alpha channel of the image
        mask = QBitmap(self.pixmap.createMaskFromColor(Qt.transparent))
        self.setMask(mask)

    def set_size_by_percentage(self, percentage):
        original_size = self.pixmap.size()
        new_width = int(original_size.width() * percentage)
        new_height = int(original_size.height() * percentage)
        self.setFixedSize(new_width, new_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # set last pressed piece
            self.parent().last_pressed_piece = self
            if not self.onboard and self.movable:  # Only allow dragging if the piece is not on the board
                self.dragging = True #IF PIECE IS ON THE BOARD, THE PIECE IS NOT DRAGGED ANYMORE
                self.offset = event.pos()
            else:
                self.dragging = False
                self.move(self.last_confirmed_position)  # Move the piece back to the last confirmed position
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            current_pos = event.windowPos().toPoint()
            new_pos = current_pos - self.offset

            new_pos.setX(max(0, min(new_pos.x(), self.parent().width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), self.parent().height() - self.height())))

            self.move(new_pos)
            start_x = int((self.x() - self.board.x() + self.board.tileSize // 2) / self.board.tileSize)
            start_y = int((self.y() - self.board.y() + self.board.tileSize // 2) / self.board.tileSize)
            can_be_placed = self.board.canPlacePiece(start_x, start_y, self)
        
            # Check if the move is possible and update the color overlay accordingly 
            if self.geometry().intersects(self.Layout.geometry()) and not self.check_collision(self.pieces) and can_be_placed:
                self.set_color_overlay(Qt.green) #MEANS THAT THE PIECE CAN BE PLACED AND COUNTS THE POINTS
            else:
                self.set_color_overlay(Qt.red) #PIECE CANNOT BE PLACED

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            if not self.onboard and self.geometry().intersects(self.Layout.geometry()) and not self.check_collision(self.pieces):
                # Store the new position but don't confirm it yet
                self.new_position = self.pos()
            # After dropping the piece, reset the color overlay to transparent
            if self.movable:
                self.set_color_overlay(Qt.transparent)

    #OVERLAY FOR THE GREEN AND RED
    def set_color_overlay(self, color):
        overlay_pixmap = QPixmap(self.pixmap.size())
        painter = QPainter(overlay_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.setOpacity(0.8)  # Set the opacity to 0.7 for non-movable pieces
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.fillRect(overlay_pixmap.rect(), color)
        painter.end()

        self.setPixmap(overlay_pixmap)


    #SELF EXPLANATORY
    def check_collision(self, pieces):
        for piece in pieces:
            if piece != self and piece.onboard and self.pixel_collision(piece):
                return True
        return False

    def pixel_collision(self, other_piece):
        # Convert the pieces' pixmaps to QImages for pixel-level collision check
        image1 = self.pixmap.toImage()
        image2 = other_piece.pixmap.toImage()

        # Calculate the intersection area between the pieces' geometries
        intersection = self.geometry().intersected(other_piece.geometry())

        # Iterate over the pixels within the intersection area
        for x in range(intersection.x(), intersection.x() + intersection.width()):
            for y in range(intersection.y(), intersection.y() + intersection.height()):
                # Calculate the corresponding positions within the images
                img1_x = x - self.geometry().x()
                img1_y = y - self.geometry().y()
                img2_x = x - other_piece.geometry().x()
                img2_y = y - other_piece.geometry().y()

                # Check if the corresponding pixels are both opaque
                if image1.pixelColor(img1_x, img1_y).alpha() > 0 and image2.pixelColor(img2_x, img2_y).alpha() > 0:
                    return True

        return False

    def rotateShape(self):
        self.shape = list(zip(*reversed(self.shape)))


    #order of pieces are the same, only need the values that changes with each move?
    def __getstate__(self):
        d = self.__dict__
        self_dict = {'dragging': d['dragging'], 'offset': d['offset'],
                     'onboard': d['onboard'], 'movable': d['movable'],
                     'last_confirmed_position': d['last_confirmed_position'],
                     'new_position':d['new_position']}
        return self_dict

    def __setstate__(self, state):
        self.__dict__ = state
