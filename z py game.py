
import sys
import subprocess

try:
    import pygame, os, json, time
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pygame"])
    import pygame, os, json, time

pygame.init()   
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("!두근두근미소녀 연애 시뮬레이터!")
clock = pygame.time.Clock()

#폰트
# 폰트 설정 (게임 시작 부분에)
font = pygame.font.SysFont("malgungothic", 40)
name_font = pygame.font.SysFont("malgungothic", 36, bold=True)
choice_font = pygame.font.SysFont("malgungothic", 32, bold=True)

# 캐릭터별 이름 색상 설정
name_colors = {
    "나": (0, 0, 255),     # 흰색
    "하루카": (255, 160, 200), # 하늘색
    "유나": (130, 200, 255), 
    "아름":(0,0,255)  # 분홍색
}

def is_choice_available(effects, love):
    """선택지의 조건(require / require_min)이 충족되었는지 확인"""
    if not isinstance(effects, dict):
        return True  # 조건이 없는 선택지는 항상 가능

    req = effects.get("require")
    req_min = effects.get("require_min", 0)

    if req and love.get(req, 0) < req_min:
        return False  # 조건 미달
    return True


def wait_for_space():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        clock.tick(30)


def get_name_position(chars, name):
    # 캐릭터가 하나면 중앙 기준으로 왼쪽
    if len(chars) == 1:
        return "left"
    # 두 명 있을 때 캐릭터 이름에 따라 결정
    if len(chars) == 2:
        if name == chars[0]:
            return "left"
        elif name == chars[1]:
            return "right"
    # 기본값
    return "left"
def draw_dialogue_box(surface, alpha=160):
    # --- 영역 정의 ---
    box_x, box_y = 72, 518
    box_w, box_h = 1280 - box_x * 2, 178
    radius = 10

    # --- 메인 박스 ---
    box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(
        box_surface,
        (0, 0, 0, alpha),
        (0, 0, box_w, box_h),
        border_radius=radius
    )

    # --- 흰색 테두리를 따로 얇게 그려서 덧씌움 ---
    border_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(
        border_surface,
        (255, 255, 255, 230),
        (0.5, 0.5, box_w - 1, box_h - 1),  # ✅ subpixel offset (삐짐 방지)
        width=1,                           # ✅ 1픽셀 정확히 내부에만 그려짐
        border_radius=radius
    )

    # --- 합성 ---
    box_surface.blit(border_surface, (0, 0))
    surface.blit(box_surface, (box_x, box_y))
def draw_name_box(surface, name, position="left"):
    name_color = name_colors.get(name, (255, 255, 255))
    text = name_font.render(name, True, name_color)
    padding_x, padding_y = 25, 8
    w, h = text.get_width() + padding_x * 2, text.get_height() + padding_y * 2

    box = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(box, (0, 0, 0, 180), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(box, (255, 255, 255, 220), (1, 1, w - 2, h - 2), 2, border_radius=10)
    box.blit(text, (padding_x, padding_y))

    x = 80 if position == "left" else 1280 - w - 80
    y = 505 - h
    surface.blit(box, (x, y))


def draw_name_box(surface, name, position="left"):
    """이름칸 — 절대 안 움직이고 테두리 안 삐져나오게 고정"""
    name_color = name_colors.get(name, (255, 255, 255))
    text = name_font.render(name, True, name_color)
    pad_x, pad_y = 25, 8
    w, h = text.get_width() + pad_x * 2, text.get_height() + pad_y * 2

    # 딱 맞는 크기의 Surface
    box = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(box, (0, 0, 0, 180), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(box, (255, 255, 255, 220), (1, 1, w - 2, h - 2), 2, border_radius=10)
    box.blit(text, (pad_x, pad_y))

    # 위치 고정 (왼쪽: 플레이어, 오른쪽: 다른 캐릭터)
    x = 80 if position == "left" else 1280 - w - 80
    y = 505 - h
    surface.blit(box, (x, y))

def draw_typing_text_with_name(surface, bg, chars, name, text, font, pos, color=(255,255,255), cps=30):
    """대사 타이핑 + 이름칸 동시 표시 (안 흔들리고 안 밀림)"""
    start_time = pygame.time.get_ticks()
    typing_done = False

    # --- 이름 위치 고정 ---
    if len(chars) == 1 or name == player["name"]:
        name_pos = "left"
    else:
        name_pos = "right"

    # --- 이름 Surface 한 번만 생성 ---
    name_color = name_colors.get(name, (255, 255, 255))
    name_text = name_font.render(name, True, name_color)
    pad_x, pad_y = 25, 8
    w, h = name_text.get_width() + pad_x * 2, name_text.get_height() + pad_y * 2

    name_box = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(name_box, (0, 0, 0, 180), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(name_box, (255, 255, 255, 220), (1, 1, w - 2, h - 2), 2, border_radius=10)
    name_box.blit(name_text, (pad_x, pad_y))

    name_x = 80 if name_pos == "left" else 1280 - w - 80
    name_y = 505 - h

    # --- 대화창 Surface ---
    dialog_box = pygame.Surface((1160, 180), pygame.SRCALPHA)
    pygame.draw.rect(dialog_box, (0, 0, 0, 160), (0, 0, 1160, 180), border_radius=15)
    pygame.draw.rect(dialog_box, (255, 255, 255, 220), (1, 1, 1158, 178), 2, border_radius=15)

    while not typing_done:
        # ① 배경/캐릭터
        surface.blit(bg, (0, 0))
        for i, c in enumerate(chars):
            if c != "none" and c in char_images:
                draw_character(c, "center" if len(chars)==1 else ("left" if i==0 else "right"))

        # ② 대화창
        surface.blit(dialog_box, (60, 510))

        # ③ 이름칸 (항상 함께 표시)
        surface.blit(name_box, (name_x, name_y))

        # ④ 타이핑 효과
        elapsed = (pygame.time.get_ticks() - start_time) / 1000
        letters = min(int(elapsed * cps), len(text))
        surface.blit(font.render(text[:letters], True, color), (pos[0], pos[1] - 20))
        pygame.display.flip()

        if letters >= len(text):
            typing_done = True

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                surface.blit(bg, (0, 0))
                for i, c in enumerate(chars):
                    if c != "none" and c in char_images:
                        draw_character(c, "center" if len(chars)==1 else ("left" if i==0 else "right"))
                surface.blit(dialog_box, (60, 510))
                surface.blit(name_box, (name_x, name_y))
                surface.blit(font.render(text, True, color), (pos[0], pos[1] - 20))
                pygame.display.flip()
                pygame.event.clear()
                typing_done = True
                break

        clock.tick(60)





def draw_typing_text(surface, bg, chars, text, font, pos, color=(255,255,255), cps=30):
    start_time = pygame.time.get_ticks()
    typing_done = False
    alpha_value = 160

    # 반투명 대화창 미리 만들기
    text_bg = pygame.Surface((1280, 200), pygame.SRCALPHA)
    text_bg.fill((0, 0, 0, alpha_value))

    while not typing_done:
        # --- ① 배경 및 캐릭터 다시 그리기 ---
        surface.blit(bg, (0, 0))
        for i, c in enumerate(chars):
            if c != "none" and c in char_images:
                draw_character(c, "center" if len(chars)==1 else ("left" if i==0 else "right"))

        # --- ② 대화창 고정 ---
        surface.blit(text_bg, (0, 520))

        # --- ③ 타이핑 텍스트 ---
        elapsed = (pygame.time.get_ticks() - start_time) / 1000.0
        letters = int(elapsed * cps)
        if letters >= len(text):
            letters = len(text)
            typing_done = True

        partial = text[:letters]
        text_x, text_y = pos
        text_y -= 25  
        surface.blit(font.render(partial, True, color), pos)
        pygame.display.flip()

        # --- ④ 이벤트 처리 ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                surface.blit(bg, (0, 0))
                for i, c in enumerate(chars):
                    if c != "none" and c in char_images:
                        draw_character(c, "center" if len(chars)==1 else ("left" if i==0 else "right"))
                surface.blit(text_bg, (0, 520))
                surface.blit(font.render(text, True, color), pos)
                pygame.display.flip()
                typing_done = True
                break

        clock.tick(60)



# 배경 로드
def load_background(path, target_size=(1280, 720)):
    img = pygame.image.load(os.path.abspath(path)).convert_alpha()
    w, h = img.get_size()
    tw, th = target_size
    scale = max(tw / w, th / h)
    new_size = (int(w * scale), int(h * scale))
    img = pygame.transform.smoothscale(img, new_size)
    x = (tw - new_size[0]) // 2
    y = (th - new_size[1]) // 2
    surface = pygame.Surface(target_size, pygame.SRCALPHA)
    surface.blit(img, (x, y))
    return surface

# 페이드 효과
def fade(surface, color=(0, 0, 0), speed=20):
    fade = pygame.Surface((1280, 720))
    fade.fill(color)
    for alpha in range(0, 255, speed):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(15)

def fade_to_white():
    fade_surface = pygame.Surface((1280, 720))
    fade_surface.fill((255, 255, 255))
    for alpha in range(0, 256, 10):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(25)

# 타이틀 화면
def show_title():
    bg = load_background("A_title_screen_screen_of_a_Korean_visual_novel_vid.png")

    # 페이드 인 효과
    for alpha in range(0, 256, 10):
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(255 - alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)

    # Enter 키 대기
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                waiting = False

        screen.blit(bg, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    # 흰색 페이드 후 다음 화면으로 전환
    fade_to_white()

# 한글 입력 지원 setup_player()
def setup_player():
    player = {"name": "", "height": 0, "intelligence": 0, "face": 0}
    stage = "name"
    text = ""
    composition = ""  # 조합 중인 글자 표시용
    font_big = pygame.font.SysFont("malgungothic", 40)

    bg = load_background("5f35b45c-c8f4-4820-bed6-0b073cdb4dba.png")
    pygame.key.start_text_input()

    while True:
        screen.blit(bg, (0, 0))

        if stage == "name":
            prompt = "당신의 이름을 입력하세요 (한글 가능):"
        elif stage == "height":
            prompt = "키를 입력하세요 (cm):"
        elif stage == "intelligence":
            prompt = "지능을 입력하세요 (0~100):"
        elif stage == "face":
            prompt = "얼굴 점수를 입력하세요 (0~100):"

        screen.blit(font_big.render(prompt, True, (255, 255, 255)), (300, 250))
        screen.blit(font_big.render(text + composition, True, (255, 200, 150)), (400, 330))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- 한글/숫자/영문 모두 TEXTINPUT으로 처리 ---
            elif e.type == pygame.TEXTINPUT:
                text += e.text
            elif e.type == pygame.TEXTEDITING:
                composition = e.text

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if stage == "name":
                        player["name"] = text.strip() or "나"
                        text = ""
                        stage = "height"
                    elif stage == "height":
                        player["height"] = int(text or 0)
                        text = ""
                        stage = "intelligence"
                    elif stage == "intelligence":
                        player["intelligence"] = int(text or 0)
                        text = ""
                        stage = "face"
                    elif stage == "face":
                        player["face"] = int(text or 0)
                        fade(screen)
                        return player
                    composition = ""
                elif e.key == pygame.K_BACKSPACE:
                    text = text[:-1]

        clock.tick(30)

# 초기 호감도 계산
def calculate_initial_love(player):
    love = {"haruka": 0, "yuna": 0, "areum": 0}
    if player["height"] >= 185:
        love["haruka"] += 100
    elif player["height"] >= 175:
        love["haruka"] += 100
    elif player["height"] >= 165:
        love["haruka"] += 100
    if player["intelligence"] >= 90:
        love["areum"] += 100
    elif player["intelligence"] >= 80:
        love["areum"] += 100
    elif player["intelligence"] >= 70:
        love["areum"] += 100
    if player["face"] >= 90:
        love["yuna"] += 100
    elif player["face"] >= 80:
        love["yuna"] += 100
    elif player["face"] >= 70:
        love["yuna"] += 100
    return love

# 실행
show_title()
player = setup_player()
love = calculate_initial_love(player)
fade(screen)
print(f"\n✅ 플레이어 설정 완료: {player}")
print(f"✅ 초기 호감도: {love}")



# 배경 로드 (비율 유지 + 화면 꽉 채우기)
def load_background(path, target_size=(1280, 720)):
    img = pygame.image.load(os.path.abspath(path)).convert_alpha()
    w, h = img.get_size()
    tw, th = target_size
    scale = max(tw / w, th / h)
    new_size = (int(w * scale), int(h * scale))
    img = pygame.transform.smoothscale(img, new_size)
    x = (tw - new_size[0]) // 2
    y = (th - new_size[1]) // 2
    surface = pygame.Surface(target_size, pygame.SRCALPHA)
    surface.blit(img, (x, y))
    return surface

#  캐릭터 로드
def load_character(path, target_height=720):
    img = pygame.image.load(os.path.abspath(path)).convert_alpha()
    w, h = img.get_size()
    ratio = target_height / h
    new_size = (int(w * ratio), int(h * ratio))
    return pygame.transform.smoothscale(img, new_size)

#  페이드 효과
def fade(surface, color=(0, 0, 0), speed=20):
    fade = pygame.Surface((1280, 720))
    fade.fill(color)
    for alpha in range(0, 255, speed):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(15)

#  이미지 로드
bg_images = {
    "school": load_background("bg_school.png"),
    "classroom": load_background("bg_classroom.png"),
    "library": load_background("bg_library.png"),
    "street": load_background("bg_street.png"),
    "room": load_background("bg_room.png"),
    "black": load_background("bg_black.png"),
    "None" : load_background("bg_None.png"),
    "shfoqkd":load_background("bg_shfoqkd.png"),
    "dnsehdwkd":load_background("bg_dnsehdwkd.png"),
    "qnfRHc":load_background("bg_qnfRHc.png"),
    "축제":load_background("bg_축제.png")
}

char_images = {
    "haruka": load_character("haruka.png", 720),
    "yuna": load_character("yuna.png", 720),
    "areum": load_character("areum.png", 720),
    "none": None
}

shown_scenes = set()




#  캐릭터 출력
def draw_character(name, side="center", alpha=255):
    if name == "none" or name not in char_images:
        return
    img = char_images[name].copy()
    img.set_alpha(alpha)
    rect = img.get_rect()
    rect.bottom = 720

    if side == "left":
        rect.centerx = 400
    elif side == "right":
        rect.centerx = 880
    else:
        rect.centerx = 640
    screen.blit(img, rect)

#  두 캐릭터 등장 (슬라이드 인)
def draw_two_characters(left_name, right_name):
    left_img = char_images[left_name]
    right_img = char_images[right_name]
    for step in range(16):
        screen.blit(bg_images[scenes[current_scene]["bg"]], (0, 0))
        left_rect = left_img.get_rect(bottom=720, centerx=360 - (15 - step) * 10)
        right_rect = right_img.get_rect(bottom=720, centerx=920 + (15 - step) * 10)
        left_img.set_alpha(step * 17)
        right_img.set_alpha(step * 17)
        screen.blit(left_img, left_rect)
        screen.blit(right_img, right_rect)
        pygame.display.flip()
        pygame.time.delay(25)

#  캐릭터 퇴장 (슬라이드 아웃)
def fade_out_two_characters(left_name, right_name):
    left_img = char_images.get(left_name)
    right_img = char_images.get(right_name)
    for step in range(15):
        screen.blit(bg_images[scenes[current_scene]["bg"]], (0, 0))
        if left_img:
            left_rect = left_img.get_rect(bottom=720, centerx=400 - step * 12)
            left_img.set_alpha(255 - step * 17)
            screen.blit(left_img, left_rect)
        if right_img:
            right_rect = right_img.get_rect(bottom=720, centerx=880 + step * 12)
            right_img.set_alpha(255 - step * 17)
            screen.blit(right_img, right_rect)
        pygame.display.flip()
        pygame.time.delay(25)

#  시나리오 로드
def load_scenes(path="dialogues.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

scenes = load_scenes()
current_scene = "sleep_end"
dialogue_index = 0 

global last_drawn_idx   
last_drawn_idx = -1

#  장면 그리기
# --- draw_scene 수정 ---
# 대사 출력 후 키 입력 대기 함수
def wait_for_space():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        clock.tick(30)

import ast  # 상단 import 구문에 추가하세요

def draw_scene(scene_name, dialogue_index):
    scene = scenes[scene_name]
    bg = bg_images[scene["bg"]]
    chars = scene.get("chars", ["none"])

    # --- 배경 및 캐릭터 출력 ---
    screen.blit(bg, (0, 0))
    for i, c in enumerate(chars):
        if c != "none" and c in char_images:
            draw_character(c, "center" if len(chars) == 1 else ("left" if i == 0 else "right"))

    # --- 대사 Tier 분기 ---
    dialogue_sets = scene["dialogues"]
    tier = "mid"
    total_love = sum(love.values())
    if total_love < 2:
        tier = "low"
    elif total_love > 12:
        tier = "high"
    lines = dialogue_sets.get(tier, [])

    # --- 대사 표시 ---
    if dialogue_index < len(lines):
        name, text = lines[dialogue_index]
        if name == "나":
            name = player["name"]
        draw_typing_text_with_name(screen, bg, chars, name, text, font, (80, 600), cps=35)

        # SPACE 대기 루프
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "quit"
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    return "next"
            clock.tick(30)

    # --- 선택지 표시 ---
    else:
        overlay = pygame.Surface((1280, 200), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        pygame.draw.rect(overlay, (255, 255, 255, 100), overlay.get_rect(), 2, border_radius=15)
        screen.blit(overlay, (0, 520))

        choices = scene.get("choices", [])
        y = 560
        available_choices = []

        for i, choice in enumerate(choices):
            # --- ① 효과 파싱 (dict 또는 문자열 모두 지원) ---
            if len(choice) >= 3:
                t, nxt, effects = choice
                if isinstance(effects, str):
                    try:
                        effects = ast.literal_eval(effects)
                    except Exception:
                        effects = {}
            elif len(choice) == 2:
                t, nxt = choice
                effects = {}
            else:
                continue

            # --- ② 조건 검사 ---
            available = is_choice_available(effects, love)

            # --- ③ 색상 설정 ---
            color = (200, 200, 255) if available else (100, 100, 100)
            text_surface = choice_font.render(f"{i + 1}. {t}", True, color)
            screen.blit(text_surface, (100, y))
            y += 40

            available_choices.append((available, nxt, effects))

        pygame.display.flip()

        # --- ④ 입력 처리 (조건 미달 시 무시) ---
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "quit"
                elif e.type == pygame.KEYDOWN and e.unicode.isdigit():
                    i = int(e.unicode) - 1
                    if 0 <= i < len(available_choices):
                        available, nxt, effects = available_choices[i]
                        if not available:
                            continue  # 조건 미달 → 무시
                        for k, v in effects.items():
                            if k in ["require", "require_min"]:
                                continue
                            if k in love:
                                love[k] += v
                        return ("change", nxt)
            clock.tick(30)




def draw_name_box_fixed(surface, name, position="left"):
    name_color = name_colors.get(name, (255, 255, 255))
    text = name_font.render(name, True, name_color)
    pad_x, pad_y = 25, 8
    w, h = text.get_width() + pad_x * 2, text.get_height() + pad_y * 2

    box = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(box, (0, 0, 0, 180), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(box, (255, 255, 255, 220), (1, 1, w - 2, h - 2), 2, border_radius=10)
    box.blit(text, (pad_x, pad_y))

    x = 80 if position == "left" else 1280 - w - 80
    y = 505 - h
    surface.blit(box, (x, y))


def draw_typing_text_only(surface, bg, chars, text, font, pos, color=(255,255,255), cps=30):
    start_time = pygame.time.get_ticks()
    typing_done = False
    letters = 0

    while not typing_done:
        elapsed = (pygame.time.get_ticks() - start_time) / 1000
        new_letters = int(elapsed * cps)
        if new_letters != letters:
            letters = min(new_letters, len(text))
            # 글자 출력 갱신
            screen_copy = surface.copy()  # 이름칸 덮지 않게 백업 후 텍스트만 덧그림
            t = font.render(text[:letters], True, color)
            screen_copy.blit(t, (pos[0], pos[1]-20))
            pygame.display.update(pygame.Rect(pos[0], pos[1]-40, 1200, 100))

        if letters >= len(text):
            typing_done = True

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                # 모든 글자 즉시 출력
                t = font.render(text, True, color)
                surface.blit(t, (pos[0], pos[1]-20))
                pygame.display.flip()
                pygame.event.clear()
                typing_done = True
                break

        clock.tick(60)

import datetime

def draw_phone_scene(screen, font, choice_font, scene, idx, typing_text):
    # ===== 배경 처리 =====
    bg_name = scene.get("bg", "phone")
    bg_path = f"{bg_name}.png"
    if os.path.exists(bg_path):
        bg_img = pygame.image.load(bg_path).convert()
        bg_img = pygame.transform.scale(bg_img, (1280, 720))
        screen.blit(bg_img, (0, 0))
    else:
        # 배경이 없을 때 대비 (흰색 밝은 배경)
        screen.fill((240, 240, 245))

    # ===== 대화 표시 =====
    lines = scene.get("dialogues", {}).get("mid", [])
    y = 150

    for i in range(min(idx + 1, len(lines))):
        name, text = lines[i]
        is_player = (name == "나")

        if is_player:
            # 오른쪽 말풍선
            bubble_rect = pygame.Rect(700, y, 500, 70)
            pygame.draw.rect(screen, (80, 160, 255), bubble_rect, border_radius=20)
            msg_surface = font.render(text if i < idx else typing_text, True, (255, 255, 255))
            screen.blit(msg_surface, (bubble_rect.x + 20, bubble_rect.y + 20))
        else:
            # 왼쪽 말풍선
            bubble_rect = pygame.Rect(80, y, 500, 70)
            pygame.draw.rect(screen, (230, 230, 230), bubble_rect, border_radius=20)
            msg_surface = font.render(text if i < idx else typing_text, True, (0, 0, 0))
            screen.blit(msg_surface, (bubble_rect.x + 20, bubble_rect.y + 20))

        y += 90

    # ===== 선택지 표시 =====
    if idx >= len(lines):
        overlay = pygame.Surface((1280, 180), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 540))

        choices = scene.get("choices", [])
        y = 560
        available_choices = []

        for i, choice in enumerate(choices):
            if len(choice) >= 3 and isinstance(choice[2], dict):
                t, nxt, effects = choice
            else:
                if len(choice) >= 2:
                    t, nxt = choice[:2]
                else:
                    continue
                effects = {}

            # 조건 확인
            req = effects.get("require")
            req_min = effects.get("require_min", 0)
            available = True
            if req and love.get(req, 0) < req_min:
                available = False

            color = (255, 255, 200) if available else (100, 100, 100)
            txt = choice_font.render(f"{i+1}. {t}", True, color)
            screen.blit(txt, (100, y))
            y += 40
            available_choices.append((available, nxt, effects))

    pygame.display.flip()



def phone_scene_loop(screen, font, choice_font, player, love, scenes):
    current_scene = "phone_scene"
    idx = 0
    typing_idx = 0
    typing_text = ""
    clock = pygame.time.Clock()

    while True:
        scene = scenes[current_scene]
        lines = scene.get("dialogues", {}).get("mid", [])
        draw_phone_scene(screen, font, choice_font, scene, idx, typing_text)

        # --- 대사 타이핑 처리 ---
        if idx < len(lines):
            _, text = lines[idx]
            if typing_idx < len(text):
                typing_text = text[:typing_idx]
                typing_idx += 1
            else:
                typing_text = text
        else:
            typing_text = ""

        # --- 이벤트 처리 ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    # 다음 대사로
                    if idx < len(lines) - 1:
                        idx += 1
                        typing_idx = 0
                        typing_text = ""
                    else:
                        # 대사 끝나면 선택지로
                        idx = len(lines)
                        typing_idx = 0
                        typing_text = ""

                elif e.key == pygame.K_ESCAPE:
                    return "ending"

                elif e.unicode.isdigit() and idx >= len(lines):
                    i = int(e.unicode) - 1
                    choices = scene.get("choices", [])
                    if 0 <= i < len(choices):
                        _, nxt, effects = choices[i]
                        if not isinstance(effects, dict):
                            effects = {}

                        # --- 조건 확인 ---
                        req = effects.get("require")
                        req_min = effects.get("require_min", 0)
                        if req and love.get(req, 0) < req_min:
                            continue  # 조건 미달이면 무시

                        # --- 효과 적용 ---
                        for k, v in effects.items():
                            if k in ["require", "require_min"]:
                                continue
                            if k in love:
                                love[k] += v

                        # --- 장면 이동 ---
                        current_scene = nxt
                        idx = 0
                        typing_idx = 0
                        typing_text = ""

                        if current_scene == "ending":
                            return "ending"

        clock.tick(30)





# 메인 루프
# 메인 루프
while True:
    result = draw_scene(current_scene, dialogue_index)

    if result == "next":
        dialogue_index += 1

    elif isinstance(result, tuple) and result[0] == "change":
        current_scene = result[1]
        dialogue_index = 0

        # ✅ 폰 장면이면 별도 루프로 진입
        if current_scene.startswith("phone"):
            phone_scene_loop(screen, font, choice_font, player, love, scenes)
            continue

    elif result == "quit":
        pygame.quit()
        sys.exit()

    clock.tick(30)


