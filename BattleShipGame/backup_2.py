import random
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd
import position


class BattleshipGame:
    def __init__(self):
        # Création de la fenêtre de menu
        self.menu_window = tk.Tk()
        self.menu_window.title("Menu Bataille Navale")
        self.loaded= False
        # Ajout des boutons pour lancer la partie et quitter le jeu
        self.start_button = tk.Button(self.menu_window, text="Lancer la partie", command=self.start_game)
        self.start_button.pack(pady=10)
        self.load_btn = tk.Button(self.menu_window, text="Load", command=self.load)
        self.load_btn.pack()
        self.quit_button = tk.Button(self.menu_window, text="Quitter", command=self.quit_game)
        self.quit_button.pack()
        
        # Création de la fenêtre de jeu
        self.root = tk.Tk()
        self.root.title("Bataille Navale")

        self.save_btn = tk.Button(self.root, text="save", command=self.save)
        self.save_btn.pack()

        self.player_ships = []
        self.current_ship_size = 2

        self.player_grid = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.player_grid.pack(side="left", padx=(30, 0))
        self.player_grid.bind("<Button-1>", self.place_ship)
        self.player_grid.bind("<Motion>", self.preview_ship)

        self.ai_grid = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.ai_grid.pack(side="right", padx=(0, 30))
        self.ai_grid.bind("<Button-1>", self.player_attack)

        for i in range(10):
            self.player_grid.create_line(0, i * 30, 300, i * 30)
            self.player_grid.create_line(i * 30, 0, i * 30, 300)
            self.ai_grid.create_line(0, i * 30, 300, i * 30)
            self.ai_grid.create_line(i * 30, 0, i * 30, 300)

        # Créer l'attribut message_label après la création des grilles
        self.message_label = tk.Label(self.root, text="Placez vos navires.", font=("Arial", 16))
        self.message_label.pack(side="bottom")
        self.place_ai_ships()
        self.root.withdraw()
        self.can_attack = False

        # Ajoutez cette ligne pour définir l'attribut player_turn
        self.player_turn = True

        # Création du menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Ajout du menu d'aide
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Aide", menu=self.help_menu)
        self.help_menu.add_command(label="Règles du jeu", command=self.show_rules)
        self.help_menu.add_command(label="À propos", command=self.show_about)
        self.ai_attacks = set()
        self.player_ships_hit = set()
        # Mettre à jour le texte de l'attribut message_label après sa création
        #self.reset_game()
        
        self.player_positions = []
        self.ai_test = 14
        #init des dataframe, avec numpy
        self.player_map = pd.DataFrame(data=np.zeros((10,10), dtype=int), dtype=int) #np.zeros cree une matrice avec 0
        self.player_attacks = pd.DataFrame(data=np.zeros((10,10), dtype=int), dtype=int)
        self.AI_attacks = pd.DataFrame(data=np.zeros((10,10), dtype=int), dtype=int)
        self.analyse = pd.read_pickle("analyse")#reads le fichier analyse

    def load(self):
        self.menu_window.withdraw()
        self.root.deiconify()
        self.load_ai_ships()
        self.load_player_attacks()
        self.load_ai_attacks()
        self.load_player_ships()
        self.player_attacks = pd.read_pickle("save_player_attacks")
        self.AI_attacks = pd.read_pickle("save_ai_attacks")
        print("loaded")
    
    #saves les attack das les fichier appro
    def save(self):
        self.player_attacks.to_pickle("save_player_attacks")
        self.AI_attacks.to_pickle("save_ai_attacks")
        print("Saved")
        print("AI Attacks : ")
        print(self.AI_attacks)
        print("Player Attacks: ")
        print(self.player_attacks)
        print("Layout :")
        print(self.player_map,"\n", self.ai_ships)

    def start_game(self):
        self.menu_window.withdraw()
        self.root.deiconify()

    def quit_game(self):
        self.root.destroy()
        
    def load_player_ships(self):
            self.player_grid.unbind("<Button-1>")
            self.player_grid.unbind("<Motion>")
            for x,y in position.get_positions(pd.read_pickle("save_player_map"),1):
                self.player_grid.create_rectangle(x*30+1, y*30+1, (x+1)*30-1, (y+1)*30-1, fill="blue", outline="")
            messagebox.showinfo("Nouvelle partie", "Que le meilleur gagne !")

    def place_ship(self, event):
        x, y = event.x // 30, event.y // 30

        shift_pressed = event.state & 0x0001 == 0x0001

        if shift_pressed:
            orientation = "vertical"
        else:
            orientation = "horizontal"

        if not self.check_collision(self.player_grid, x, y, self.current_ship_size, orientation):
            return
        for i in range(self.current_ship_size):
            if orientation == "horizontal":
                self.player_grid.create_rectangle((x+i)*30+1, y*30+1, (x+i+1)*30-1, (y+1)*30-1, fill="blue", outline="")
                self.player_map.at[x+i,y] = 1
                self.player_positions.append((x+i,y))
            elif orientation == "vertical":
                self.player_grid.create_rectangle(x*30+1, (y+i)*30+1, (x+1)*30-1, (y+i+1)*30-1, fill="blue", outline="")
                self.player_map.at[x,y+i] = 1
                self.player_positions.append((x,y+i))
        self.player_ships.append((x, y, self.current_ship_size, orientation))
        self.player_map.to_pickle("save_player_map")

        self.current_ship_size += 1

        if self.current_ship_size > 5:
            self.player_grid.unbind("<Button-1>")
            self.player_grid.unbind("<Motion>")
            messagebox.showinfo("Nouvelle partie", "Que le meilleur gagne !")

            # Vérifier si tous les navires ont été placés pour autoriser les attaques
            if len(self.player_ships) == 5:
                self.can_attack = True

            # Mettre à jour le texte de l'attribut message_label pour indiquer que les attaques sont autorisées
            self.message_label.config(text="Attaquez l'adversaire !")





    def preview_ship(self, event):
        x, y = event.x // 30, event.y // 30

        shift_pressed = event.state & 0x0001 == 0x0001
        if shift_pressed:
            orientation = "vertical"
        else:
            orientation = "horizontal"

        self.player_grid.delete("preview")

        if len(self.player_ships) == 5:
            return

        if not self.check_collision(self.player_grid, x, y, self.current_ship_size, orientation):
            return

        for i in range(self.current_ship_size):
            if orientation == "horizontal":
                self.player_grid.create_rectangle((x+i)*30+1, y*30+1, (x+i+1)*30-1, (y+1)*30-1, fill="blue", outline="", tags="preview")
            elif orientation == "vertical":
                self.player_grid.create_rectangle(x*30+1, (y+i)*30+1, (x+1)*30-1, (y+i+1)*30-1, fill="blue", outline="", tags="preview")

    #Permet d'avoire l'acien layout
    def load_player_attacks(self):
        for x,y in position.get_positions(pd.read_pickle("save_player_attacks"),1):
            if self.ai_ships[x,y] == 1:
                self.ai_grid.create_oval(x * 30 + 10, y * 30 + 10, x * 30 + 20, y * 30 + 20, fill="red")
            else:
                self.ai_grid.create_oval(x * 30 + 10, y * 30 + 10, x * 30 + 20, y * 30 + 20, fill="white")
                self.player_ships_hit.add((x, y))

    def player_attack(self, event):
        if not self.player_turn:
            return

        x, y = event.x // 30, event.y // 30
        self.player_attacks.at[x,y]=1

        if  self.ai_ships[x,y] == 1:
            self.ai_grid.create_oval(x * 30 + 10, y * 30 + 10, x * 30 + 20, y * 30 + 20, fill="red")
            self.ai_test -=1
            if  self.ai_test == 0:
                messagebox.showinfo("Victoire", "Félicitations, vous avez gagné !")
            else:
                self.player_turn = True  # Ajoutez cette ligne pour réinitialiser self.player_turn
                self.ai_attack()
        else:
            self.ai_grid.create_oval(x * 30 + 10, y * 30 + 10, x * 30 + 20, y * 30 + 20, fill="white")
            self.player_ships_hit.add((x, y))
            self.player_turn = False
            self.ai_attack()



    def show_rules(self):
        messagebox.showinfo("Règles du jeu", "Les règles du jeu sont...")

    def show_about(self):
        messagebox.showinfo("A propos de...", "Bataille Navale version 1.0\nCréé par John Doe")

    def load_ai_ships(self):
        self.ai_ships = pd.read_pickle("save_ai_map").to_numpy()#to numpy pour la transfor en matrice numpy
        
    def place_ai_ships(self):
        self.ai_ships = np.zeros((10,10), dtype=int)

        for size in [5, 4, 3, 2]:
            orientation = random.choice(["horizontal","vertical"])
            to_place = True
            
            while to_place:
                if orientation == "horizontal":
                    x,y = random.randint(0,9), random.randint(0,10-size)
                    if not (1 in self.ai_ships[x][y:y+size]):
                        to_place=False
                        self.ai_ships[x][y:y+size] = 1
                else:
                    x,y = random.randint(0,10-size), random.randint(0,9)
                    Transposite = self.ai_ships.T
                    if not (1 in Transposite[y][x:x+size]):
                        to_place=False
                        Transposite[y][x:x+size] = 1
                        self.ai_ships = Transposite.T
        pd.DataFrame(data=self.ai_ships, dtype=int).to_pickle("save_ai_map")#save les bateau de l'ia, self.ai_ships represente layout,
        #appre creation de layout save in dataframe



    def reset_game(self):
        # Réinitialiser les ensembles des attaques et des navires touchés
        self.ai_attacks = set()
        self.player_ships_hit = set()

        # Réinitialiser la taille du navire en cours de placement
        self.current_ship_size = 2

        # Effacer les grilles du joueur et de l'IA
        for grid in [self.player_grid, self.ai_grid]:
            for x in range(10):
                for y in range(10):
                    grid.create_rectangle(x*30+1, y*30+1, (x+1)*30-1, (y+1)*30-1, fill="", outline="")

        # Effacer les navires du joueur et de l'IA
        self.player_ships = []
        self.ai_ships = []

        # Placer les navires de l'IA
        self.place_ai_ships()

        # Réactiver la possibilité de placer des navires pour le joueur
        self.player_grid.bind("<Button-1>", self.place_ship)

        # Vérifier que l'attribut message_label est défini avant de l'utiliser
        if hasattr(self, "message_label"):
            self.message_label.config(text="Placez vos navires.")

    #load les attack fait par l'ia
    def load_ai_attacks(self):
        for x,y in position.get_positions(pd.read_pickle("save_ai_attacks"),1):
            self.player_grid.create_line(x*30+5, y*30+5, (x+1)*30-5, (y+1)*30-5, fill="gray")
            self.player_grid.create_line(x*30+5, (y+1)*30-5, (x+1)*30-5, y*30+5, fill="gray")
            
    def ai_attack(self):
        if not self.player_turn:
            hit = False  # Initialisez hit à False à chaque itération
            
            while not hit:
                pos = position.get_positions(self.analyse,self.analyse.values.max())
                if len(pos) == 1:
                    (x,y) = pos[0]
                else:
                    (x, y) = random.choice(pos)
                self.analyse.at[x,y] = -1
                
                while (x, y) in self.ai_attacks:
                    x, y = random.randint(0, 9), random.randint(0, 9)
                    
                self.ai_attacks.add((x, y))
                self.AI_attacks.at[x,y] =1

                if (x, y) in self.player_positions:
                    self.player_grid.create_rectangle(x*30+1, y*30+1, (x+1)*30-1, (y+1)*30-1, fill="red", outline="")
                    print("hit")
                    dt = pd.read_pickle("analyse")
                    dt.at[x,y] +=1      #ajoute un points si la position a un ship
                    dt.to_pickle("analyse")
                    self.player_ships_hit.add((x, y))
                    
                    if len(self.player_ships_hit) == len(self.player_ships):
                        messagebox.showinfo("Fin de la partie", "L'IA a gagné !")
                        self.reset_game()
                    else:
                        self.player_turn = False
                    hit = True  # Mettez hit à True si l'IA touche un bateau
                    self.player_turn = True
                else:
                    self.player_grid.create_line(x*30+5, y*30+5, (x+1)*30-5, (y+1)*30-5, fill="gray")
                    self.player_grid.create_line(x*30+5, (y+1)*30-5, (x+1)*30-5, y*30+5, fill="gray")
                    hit = True  # Mettez hit à True seulement si vous manquez une cible
                    self.player_turn = True
                    





    def check_collision(self, grid, x, y, size, orientation):
        if orientation == "horizontal":
            if x + size > 10:
                return False
            for i in range(size):
                if (x+i, y) in self.occupied_cells():
                    return False
        elif orientation == "vertical":
            if y + size > 10:
                return False
            for j in range(size):
                if (x, y+j) in self.occupied_cells():
                    return False
        if x < 0 or x > 9 or y < 0 or y > 9:
            return False
        return True
    
    def occupied_cells(self):
        occupied = set()
        for ship in self.player_ships:
            x, y, size, orientation = ship
            for i in range(size):
                if orientation == "horizontal":
                    occupied.add((x+i, y))
                elif orientation == "vertical":
                    occupied.add((x, y+i))
        return occupied



    # (Les autres méthodes nécessaires vont ici, telles que check_collision, place_ai_ships, etc.)


    def mainloop(self):
        self.menu_window.mainloop()
        self.root.mainloop()


if __name__ == "__main__":
    game = BattleshipGame()
    game.mainloop()