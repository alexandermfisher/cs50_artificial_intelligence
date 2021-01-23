import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        ### Any time the number of cells is equal to the count, we know that all of that sentence’s cells must be mines.
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        ### Any time the count is equal to 0, we know that all of that sentence’s cells must be safe.
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

    def is_subset(self, other_sentence):
        ## tests to see if it is a subset of other sentence.
        ## returns true if yes it is or false if no it is not.
        if self.cells != other_sentence.cells and self.cells.issubset(other_sentence.cells):
            return True
        else:
            return False

    def infer_new_sentance(self, other_sentence):
        ### where self.cells is a subset of other_sentence.cells a new sentence is made
        different_cells = other_sentence.cells.difference(self.cells)
        different_count = other_sentence.count - self.count
        new_sentence = Sentence(different_cells, different_count)

        return new_sentence


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        ## form new sentance and add to knowledge base
        neibouring_cells = set()
        for i in range(max(0, cell[0]-1), min(cell[0] + 2, self.height)):
            for j in range(max(0, cell[1]-1), min(cell[1] + 2, self.width)):
                # Add the cell clicked on to moves made and safe set sets
                if (i, j) == cell:
                    self.moves_made.add(cell)
                    self.mark_safe(cell)
                else:
                    neibouring_cells.add((i,j))

        new_sentence = Sentence(neibouring_cells, count)
        ## marks mines and safes for new sentance.
        for mine in self.mines:
            new_sentence.mark_mine(mine)
        for safe in self.safes:
            new_sentence.mark_safe(safe)

        ## add new sentence to knowledge base.
        self.knowledge.append(new_sentence)

        """
        update knowledge base in any inferneces can be made.
        while any one of the three inference moves can generate new knowledge or ascribe a
        cell as a mine or safe this loop will continue (i.e. until no more inferences can be
        made and all new knowledge genereated by the new sentence/cell has been accounted for.)
        """
        while self.inference_1() or self.inference_2() or self.inference_3():

            # find any subsetting possibilities and update knowledge base.
            for sentence_1 in self.knowledge.copy():
                for sentence_2 in self.knowledge.copy():
                    if sentence_1.is_subset(sentence_2):
                        new_sentence = sentence_1.infer_new_sentance(sentence_2)
                        self.knowledge.append(new_sentence)
                        self.knowledge.remove(sentence_2)

            # find any known mines or safes sentences and update mines and safes set
            for sentence in self.knowledge:
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)

            # remove all empty sets in knowledge
            for sentence in self.knowledge:
                if sentence.cells == set():
                    self.knowledge.remove(sentence)

    """
    These three infernce functions loop over all sentences in knowledge and retrun
    a list of sentences that result from the relevant inferneces rules. If any of the
    three lists is not empty a infernece can be made and the subsequent knowledge can be added to knowledge bank.
    They are used in for the while loops condition to check if any inferneces can be made.
    I.e. While inferneces can be made they will be made and knowledge will be updated.
    """

    def inference_1(self):
        """
        Returns a list of new sentences, that can be formed by sub set infernece rule.
        That is to say if a sentence.cells is a subset of another sentance.cells, then the
        differnce will be found and the count will be calculated and a new sentance will
        be added to a list that will be returned.

        knowledge must be a list of Sentences()
        """
        new_sentences = []
        for sentence_1 in self.knowledge:
            for sentence_2 in self.knowledge:
                if sentence_1.is_subset(sentence_2):
                    new_sentence = sentence_1.infer_new_sentance(sentence_2)
                    new_sentences.append(new_sentence)
        return new_sentences

    def inference_2(self):
        """
        Returns a list of sentances where there are known safes. I.e where sentance.count = 0 and all cells are therefore safe.
        """
        safe_sentences = []
        for sentence in self.knowledge:
            if sentence.known_safes() != set():
                safe_sentences.append(sentence)
        return safe_sentences

    def inference_3(self):
        """
        Returns a list of sentences where there are known mines. I.e. where  length of set is equal to count, and all cells are therefore a mine.
        """
        mine_sentences = []
        for sentence in self.knowledge:
            if sentence.known_mines() != set():
                mine_sentences.append(sentence)
        return mine_sentences

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made and move not in self.mines:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        for i in range(0, self.height):
            for j in range(0, self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    possible_moves.append(move)

        ### if available move, randomly pick one and return move, else return None as no move available.
        if possible_moves:
            random_index = random.randint(0,len(possible_moves)-1)
            random_move = possible_moves[random_index]
            return random_move
        else:
            return None
