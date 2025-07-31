import pygame
import random
import math

# --- Oyun Ayarları ve Sabitler ---
EKRAN_GENISLIGI = 500
EKRAN_YUKSEKLIGI = 700
FPS = 60

# Renkler
SIYAH = (0, 0, 0)
BEYAZ = (255, 255, 255)
ARKA_PLAN = (20, 20, 40)
KUTU_RENGI = (40, 40, 60)
FAUL_CIZGI_RENGI = (255, 100, 100)
YAZI_RENGI = (220, 220, 220)

# Oyun Alanı Ayarları
KUTU_X = 50
KUTU_GENISLIK = 400
KUTU_YUKSEKLIK = 600
KUTU_Y = EKRAN_YUKSEKLIGI - KUTU_YUKSEKLIK
FAUL_CIZGI_Y = KUTU_Y + 50

# Fizik Ayarları
YER_CEKIMI = 0.2
FIZIK_ITERASYONLARI = 6
BOUNCINESS = 0.8

# Topların Özellikleri
TOP_OZELLIKLERI = {
    2:    {'radius': 15, 'color': (100, 200, 255)}, 4:    {'radius': 18, 'color': (100, 255, 200)},
    8:    {'radius': 22, 'color': (255, 255, 100)}, 16:   {'radius': 26, 'color': (255, 200, 100)},
    32:   {'radius': 30, 'color': (255, 150, 100)}, 64:   {'radius': 35, 'color': (255, 100, 100)},
    128:  {'radius': 40, 'color': (255, 100, 200)}, 256:  {'radius': 45, 'color': (200, 100, 255)},
    512:  {'radius': 50, 'color': (150, 100, 255)}, 1024: {'radius': 55, 'color': (100, 100, 255)},
    2048: {'radius': 60, 'color': (200, 200, 200)},
}

class Top(pygame.sprite.Sprite):
    def __init__(self, x, y, value, is_static=False):
        super().__init__()
        self.value = value
        ozellikler = TOP_OZELLIKLERI[self.value]
        self.radius = ozellikler['radius']
        self.color = ozellikler['color']
        self.mass = self.value
        
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0 
        self.is_static = is_static
        
        self.font = pygame.font.Font(None, int(self.radius * 0.9))
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        self.ustte_kalma_sayaci = 0

    def update(self):
        if not self.is_static:
            self.vx *= 0.998
            self.vy *= 0.998
            self.vy += YER_CEKIMI
            self.x += self.vx
            self.y += self.vy
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        text_surf = self.font.render(str(self.value), True, SIYAH)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)

def generate_next_top():
    degerler = [2, 4, 8, 16]
    agirliklar = [12, 6, 3, 1]
    value = random.choices(degerler, weights=agirliklar)[0]
    return Top(EKRAN_GENISLIGI / 2, KUTU_Y - 40, value, is_static=True)

def oyun():
    pygame.init()
    ekran = pygame.display.set_mode((EKRAN_GENISLIGI, EKRAN_YUKSEKLIGI))
    pygame.display.set_caption("2048 Balls")
    saat = pygame.time.Clock()
    font_buyuk = pygame.font.Font(None, 60)
    font_orta = pygame.font.Font(None, 48)
    font_kucuk = pygame.font.Font(None, 36)

    oyun_basladi = False
    oyun_bitti = False
    toplar = pygame.sprite.Group()
    current_top = generate_next_top()
    next_top_preview = generate_next_top()
    skor = 0

    calisiyor = True
    while calisiyor:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if oyun_bitti:
                    oyun()
                    return
                if not oyun_basladi:
                    oyun_basladi = True
                elif current_top:
                    current_top.is_static = False
                    toplar.add(current_top)
                    current_top = next_top_preview
                    next_top_preview = generate_next_top()

        if current_top and current_top.is_static and oyun_basladi and not oyun_bitti:
               mouse_x = pygame.mouse.get_pos()[0]
               radius = current_top.radius
               current_top.x = max(KUTU_X + radius, min(mouse_x, KUTU_X + KUTU_GENISLIK - radius))

        if oyun_basladi and not oyun_bitti:
            toplar.update()
            all_balls_list = toplar.sprites()
            for _ in range(FIZIK_ITERASYONLARI):
                for top in all_balls_list:
                    if top.x - top.radius < KUTU_X: top.x, top.vx = KUTU_X + top.radius, top.vx * -BOUNCINESS
                    elif top.x + top.radius > KUTU_X + KUTU_GENISLIK: top.x, top.vx = KUTU_X + KUTU_GENISLIK - top.radius, top.vx * -BOUNCINESS
                    
                    # --- DEĞİŞTİRİLDİ: Üstel zıplama azaltma formülü ---
                    if top.y + top.radius > KUTU_Y + KUTU_YUKSEKLIK:
                        top.y = KUTU_Y + KUTU_YUKSEKLIK - top.radius
                        seviye = math.log2(top.value)
                        azaltma_faktoru = (math.sqrt(2)) ** (seviye - 1)
                        mass_adjusted_bounciness = BOUNCINESS / azaltma_faktoru
                        top.vy *= -mass_adjusted_bounciness
                
                # Top çarpışmaları ve birleşme... (Bu kısım aynı)
                top_to_add = []; top_to_remove = set()
                for i in range(len(all_balls_list)):
                    for j in range(i + 1, len(all_balls_list)):
                        t1, t2 = all_balls_list[i], all_balls_list[j]
                        if t1 in top_to_remove or t2 in top_to_remove: continue
                        dx, dy = t2.x - t1.x, t2.y - t1.y; dist = math.hypot(dx, dy)
                        if dist < t1.radius + t2.radius:
                            if t1.value == t2.value and t1.value < 2048:
                                top_to_remove.add(t1); top_to_remove.add(t2)
                                new_x, new_y, new_val = (t1.x+t2.x)/2, (t1.y+t2.y)/2, t1.value*2
                                top_to_add.append(Top(new_x, new_y, new_val)); skor += new_val
                                break
                            if dist == 0: dist = 0.001
                            overlap = (t1.radius + t2.radius) - dist; nx, ny = dx/dist, dy/dist
                            t1.x -= overlap/2*nx; t1.y -= overlap/2*ny; t2.x += overlap/2*nx; t2.y += overlap/2*ny
                            k_x, k_y = t1.vx-t2.vx, t1.vy-t2.vy; p = 2.0 * (nx*k_x+ny*k_y) / (t1.mass+t2.mass)
                            t1.vx-=p*t2.mass*nx*BOUNCINESS; t1.vy-=p*t2.mass*ny*BOUNCINESS
                            t2.vx+=p*t1.mass*nx*BOUNCINESS; t2.vy+=p*t1.mass*ny*BOUNCINESS
                if top_to_remove:
                    toplar.remove(*list(top_to_remove)); toplar.add(*top_to_add); all_balls_list = toplar.sprites()
            
            for top in toplar:
                if not top.is_static and top.y - top.radius < FAUL_CIZGI_Y:
                    top.ustte_kalma_sayaci += 1
                    if top.ustte_kalma_sayaci > FPS:
                        oyun_bitti = True
                        break
                else:
                    top.ustte_kalma_sayaci = 0

        # Çizim... (Bu kısım aynı)
        ekran.fill(ARKA_PLAN)
        pygame.draw.rect(ekran, KUTU_RENGI, (KUTU_X, KUTU_Y, KUTU_GENISLIK, KUTU_YUKSEKLIK))
        pygame.draw.line(ekran, FAUL_CIZGI_RENGI, (KUTU_X, FAUL_CIZGI_Y), (KUTU_X + KUTU_GENISLIK, FAUL_CIZGI_Y), 3)
        for top in toplar: top.draw(ekran)
        if oyun_bitti:
            oyun_bitti_yazi1 = font_buyuk.render("Oyun Bitti!", True, FAUL_CIZGI_RENGI)
            oyun_bitti_yazi2 = font_kucuk.render("Tekrar Başlamak için Tıkla", True, YAZI_RENGI)
            ekran.blit(oyun_bitti_yazi1, oyun_bitti_yazi1.get_rect(center=(EKRAN_GENISLIGI/2, EKRAN_YUKSEKLIGI/2 - 30)))
            ekran.blit(oyun_bitti_yazi2, oyun_bitti_yazi2.get_rect(center=(EKRAN_GENISLIGI/2, EKRAN_YUKSEKLIGI/2 + 20)))
        elif not oyun_basladi:
            basla_yazi = font_orta.render("Başlamak için Tıkla", True, YAZI_RENGI)
            ekran.blit(basla_yazi, basla_yazi.get_rect(center=(EKRAN_GENISLIGI/2, EKRAN_YUKSEKLIGI/2)))
        else:
            if current_top: current_top.draw(ekran)
            skor_yazisi = font_kucuk.render(f"Skor: {skor}", True, YAZI_RENGI)
            ekran.blit(skor_yazisi, (KUTU_X, KUTU_Y - 40))
        pygame.display.flip()
        saat.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    oyun()