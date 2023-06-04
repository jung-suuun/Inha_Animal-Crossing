import glob  # 파일 검색을 위해 사용 (유저 데이터 처리)
import sys  # 시스템별 매개변수와 함수를 사용하기 위해 사용 (ex. sys.exit())
import cv2  # 이미지 처리를 위한 OpenCV 라이브러리
import time  # 시간 관련 함수
import random  # 랜덤 값 생성을 위해 사용
from datetime import datetime  # 날짜 설정을 위해서 사용
from tkinter import Tk, Canvas, NW, font, Toplevel, messagebox, simpledialog  # 게임의 GUI 틀을 담당할 tkinter 라이브러리
from PIL import Image, ImageTk  # 파이썬 이미징 라이브러리(tkinter에서 이미지를 띄우기 위해서 사용)
from dateutil.relativedelta import relativedelta  # 달 계산을 위해서 relativedelta 사용. (1달씩 계산하려면 필요)


# 물고기 떡밥 클래스 정의
class FishFood:
    def __init__(self, name, prob):
        self.name = name  # 떡밥 이름
        self.prob = prob  # 각 떡밥마다 줄 확률 가중치 설정 (떡밥 랜덤 설정 기능 추가 시 사용 예정)


# 물고기 클래스 정의
class Fish:
    def __init__(self, name, prob, min_size, max_size, months, video_file, price, plus_money, a_prob, b_prob, c_prob):
        self.name = name  # 물고기 이름
        self.prob = prob  # 물고기가 잡힐 확률
        self.min_size = min_size  # 물고기 최소 크기
        self.max_size = max_size  # 물고기 최대 크기
        self.months = months  # 물고기가 나타나는 달의 범위
        self.video_file = video_file  # 물고기 동영상 파일명
        self.price = price  # 물고기의 가격
        self.plus_money = plus_money  # 물고기의 크기에 따라 더해줄 추가금
        self.a_prob = a_prob  # 갯지렁이 선호도
        self.b_prob = b_prob  # 물고기찌 선호도
        self.c_prob = c_prob  # 옥수수전분 선호도


# GUI 화면 클래스 정의
class FishingGUI:
    def __init__(self, master):
        # GUI 및 디스플레이 관련 설정
        self.master = master  # Tkinter의 root 객체를 저장함(화면 구성)
        self.master.title("모여봐요 인하의 숲")  # 창 상단 제목 설정
        self.canvas = Canvas(self.master, width=720, height=480)  # 720x480의 메인 캔버스 생성
        self.canvas.pack()  # 캔버스를 화면에 배치
        self.setup_video()  # 비디오 설정 메소드 호출
        self.bind_events()  # 입력 이벤트 바인딩하는 메소드 호출
        self.date_display = None  # 날짜 디스플레이
        self.money_display = None  # 돈 디스플레이
        self.fishfood_display = None  # 떡밥 종류 디스플레이
        self.fish_display = None  # 마지막으로 잡은 물고기 디스플레이
        self.ending_video_played = False  # 엔딩 영상이 재생되었는지 여부 체크

        # 도감 관련 설정
        self.fishbook_fish = []  # 도감으로 넘겨줄 리스트 (중복을 제외한 물고기 이름만 넘겨줌)
        self.catalog_visible = False  # 도감 창 노출 여부 (초기값 - 비활성화)
        self.info_window = None  # 도감 상세 정보 창 설정
        self.catalog_window = None  # 도감 메인 창 설정
        self.trophy_displayed = False  # 도감 트로피가 표시 되었는지 여부 (초기값 - 비활성화)

        # 게임 플레이 관련 변수
        self.current_date = datetime(2023, 1, 1)  # 초기 날짜 설정
        self.caught_fish = []  # 잡은 물고기를 저장할 리스트
        self.fish_display_list = [(0, 0)]  # 잡은 물고기를 저장할 리스트(GUI 출력용)
        self.user_data = {}  # 유저 데이터를 저장할 딕셔너리
        self.total_money = 0  # 초기 돈 설정
        self.fish_food_list = self.create_fish_food_list()  # 떡밥 종류 리스트 생성
        self.fish_food_index = 0  # 현재 선택된 떡밥의 인덱스 (초기값 0, 갯지렁이)
        self.cast_time = None  # 낚싯대를 던진 시간 저장
        self.last_click = None  # 마지막 마우스 클릭이 들어왔던 시간을 저장 (낚시 성공 여부 판별)
        self.click_allowed = False  # 클릭을 허용할 지 여부




    # =========== 게임 시작 메시지 창 GUI ============
    # 새 게임 불러올 지 체크
    def show_initial_screen(self):
        choice = messagebox.askyesno("모여봐요 인하의 숲", "새 게임을 시작하시겠습니까?")  # 선택 창 띄우기
        if choice:  # Yes 클릭 시
            self.start_new_game()  # 새 게임 시작
        else:  # Cancel 클릭 시
            self.load_game()  # 저장된 게임 불러오기

    # 새 게임 시작
    def start_new_game(self):
        # 사용자 이름 텍스트로 입력받아 username에 저장
        username = simpledialog.askstring("모여봐요 인하의 숲", "사용자 이름을 입력하세요.")
        # username에 값이 들어있다면 (입력이 정상적으로 들어왔다면)
        if username is not None:
            if username.strip() != "":
                # 기존에 저장된 데이터와 유저 닉네임 비교
                load_usernames = [data["username"] for data in self.load_username()]
                # 기존 데이터에 중복되는 이름이 있다면
                if username in load_usernames:
                    # 에러 메시지 출력하고 처음으로 돌아감
                    messagebox.showerror("모여봐요 인하의 숲", "해당 사용자 이름은 이미 존재합니다. 다른 이름을 입력해주세요.")
                    self.start_new_game()
                else:
                    # 중복되는 이름이 없다면 user_data를 생성 / 유저 이름, 잡은 물고기 정보, 돈, 트로피 노출여부(업적), 엔딩 달성여부
                    self.user_data = {"username": username, "caught_fish": [], "total_money": 0,
                                      "trophy_displayed": False, "ending": False}
                    self.unbind_events()  # 입력 이벤트 안 받도록 함
                    self.play_video(self.video5)  # 인트로 동영상 재생
                    self.bind_events()  # 다시 입력 이벤트 허용
                    self.start()  # 게임 시작
                    self.update_display()  # 디스플레이 업데이트
            else:
                messagebox.showerror("모여봐요 인하의 숲", "사용자 이름을 입력해야 합니다.")  # 사용자 이름을 아무것도 입력하지 않을 경우
                self.start_new_game()  # 처음으로 돌아감
        else:
            self.show_initial_screen()  # cancel을 누를 시 이전 화면을 돌아감

    # 기존 게임 불러오기
    def load_game(self):
        username = simpledialog.askstring("모여봐요 인하의 숲", "불러올 사용자 이름을 입력하세요.")  # 유저 이름을 입력받음
        if username is None:  # 사용자가 취소 버튼을 눌렀거나 창을 닫았을 경우
            self.show_initial_screen()  # 초기화면으로 돌아감
        else:
            try:
                with open(f"{username}_data.txt", "r") as file:  # username_data.txt 파일을 읽기 모드로 가져와서 읽음
                    data = file.read()
                    self.user_data = eval(data)  # 파일에서 읽은 데이터를 딕셔너리로 변환
                    self.caught_fish = self.user_data.get("caught_fish", [])  # 잡은 물고기 정보를 가져옴
                    self.total_money = self.user_data.get("total_money", 0)  # 돈 정보를 가져옴
                    self.current_date = datetime.strptime(self.user_data.get("current_date", "2023-01-01"),
                                                          "%Y-%m-%d")  # 현재 날짜를 가져옴
                    self.trophy_displayed = self.user_data.get("trophy_displayed", '')  # 트로피 노출여부를 가져옴
                    self.ending_video_played = self.user_data.get("ending", '')  # 엔딩 달성여부를 가져옴
                    self.update_display()  # 디스플레이 업데이트
                    self.start()  # 게임 시작
            except FileNotFoundError:  # 파일을 읽을 수 없는 경우(에러 발생 시)
                messagebox.showerror("모여봐요 인하의 숲", "해당 사용자의 저장된 데이터가 없습니다.")
                self.load_game()  # 불러오기 초기 화면으로 다시 이동

    # 게임 종료 질문
    def confirm_exit(self, event):
        choice = messagebox.askyesno("게임 종료", "게임을 종료하시겠습니까?")
        # Yes 선택 시
        if choice:
            self.save_user_data()  # 유저 데이터 저장
            self.exit_program()  # 프로그램 종료 함수 호출

    # 게임 종료
    def exit_program(self):
        self.canvas.forget()  # 메인 gui 창 닫기
        self.canvas.destroy()  # 메인 gui 창 닫기
        sys.exit()  # 프로그램 종료




    # =========== 유저 데이터 처리 ============
    # 게임 저장
    def save_user_data(self):
        username = self.user_data["username"]
        self.user_data["current_date"] = self.current_date.strftime("%Y-%m-%d")  # 날짜 데이터 업데이트
        self.user_data["caught_fish"] = self.caught_fish  # 잡은 물고기 목록 업데이트
        self.user_data["total_money"] = self.total_money  # 돈 정보 업데이트
        self.user_data["trophy_displayed"] = self.trophy_displayed  # 트로피 노출여부 업데이트
        self.user_data["ending"] = self.ending_video_played  # 엔딩 달성여부 업데이트
        with open(f"{username}_data.txt", "w") as file:  # username_data.txt에 업데이트 된 정보를 덮어쓰기
            file.write(str(self.user_data))

    # 새 게임 시작 시 중복 닉네임을 비교하기 위해 username 불러오기
    def load_username(self):
        user_data_list = []  # 데이터를 저장할 빈 리스트를 생성
        for filename in glob.glob("*_data.txt"):  # 현재 디렉토리에서 "_data.txt"로 끝나는 파일들을 모두 찾음
            with open(filename, "r") as file:  # 파일을 읽기 모드로 연다
                data = file.read()  # 파일의 내용을 읽어서 data 변수에 저장
                user_data = eval(data)  # 파일에서 읽은 데이터를 딕셔너리로 변환
                user_data_list.append(user_data)  # 변환된 데이터를 리스트에 추가
        return user_data_list  # 데이터가 추가된 리스트를 return (전체 리스트가 return 됨)




    # =========== 물고기 생성 관련 ============
    # 물고기 떡밥 생성
    def create_fish_food_list(self):
        # 떡밥의 종류는 갯지렁이, 옥수수전분, 물고기찌 총 세 가지.
        fish_food_list = [
            FishFood("갯지렁이", 0.40),  # 뒤에 있는 가중치는 추후 떡밥 랜덤 선택 로직 추가 시 사용예정
            FishFood("옥수수전분", 0.35),
            FishFood("물고기찌", 0.25)
        ]
        # 생성된 떡밥 리스트를 return
        return fish_food_list

    # 다음 떡밥 선택 함수
    def select_next_fish_food(self):
        self.fish_food_index += 1  # 떡밥 인덱스를 1 증가시킴
        # 떡밥 리스트의 길이보다 길거나 같아지면 0으로 만들어 다시 처음 떡밥을 선택할 수 있게 함
        if self.fish_food_index >= len(self.fish_food_list):
            self.fish_food_index = 0
        return self.fish_food_list[self.fish_food_index]  # 선택한 떡밥을 반환

    # 현재 날짜에 맞는 물고기 리스트 생성
    def create_fish_list(self, current_month):
        fish_list = [
            # 물고기 이름, 확률 가중치, 최소길이, 최대길이, 등장 날짜(달), 비디오파일 경로, 기본 가격, 최대추가금, 갯지렁이 선호도, 옥수수전분 선호도, 물고기찌 선호도 순서
            Fish("잉어", 0.25, 21, 122, range(1, 13), 'video/잉어.mp4', 300, 200, 0.4, 0.1, 0.5),
            Fish("금붕어", 0.1, 13, 40, range(1, 13), 'video/금붕어.mp4', 1300, 300, 0.7, 0.2, 0.1),
            Fish("툭눈금붕어", 0.1, 15, 40, range(1, 13), 'video/툭눈금붕어.mp4', 1300, 300, 0.5, 0.3, 0.2),
            Fish("난주", 0.04, 5, 20, range(1, 13), 'video/난주.mp4', 4500, 500, 0.35, 0.05, 0.6),
            Fish("송사리", 0.2, 1, 4, range(4, 9), 'video/송사리.mp4', 300, 200, 0.35, 0.6, 0.05),
            Fish("가재", 0.1, 9, 20, range(4, 10), 'video/가재.mp4', 200, 100, 0.6, 0.3, 0.1),
            Fish("올챙이", 0.1, 1, 5, range(3, 8), 'video/올챙이.mp4', 100, 30, 0.1, 0.9, 0.0),
            Fish("개구리", 0.1, 6, 16, range(5, 9), 'video/개구리.mp4', 120, 50, 0.1, 0.9, 0.0),
            Fish("가물치", 0.01, 45, 180, range(6, 9), 'video/가물치.mp4', 5500, 1000, 0.35, 0.05, 0.6)
        ]
        # 현재 날짜에 해당하는 물고기만 반환
        return [fish for fish in fish_list if current_month in fish.months]

    # 크기에 따른 추가금 계산
    def special_price(self, fish, size):
        # 최대 크기인 경우
        if size == fish.max_size:
            price = fish.price + fish.plus_money  # 추가금을 전부 더함
        # 물고기 크기가 (최소 크기 + 최대 크기 / 2) 한 값보다 큰 경우
        elif size > (fish.min_size + fish.max_size) / 2:
            price = fish.price + fish.plus_money / 2  # 추가금을 반만 더함
        # 그 외의 경우 (작은 경우)
        else:
            price = fish.price  # 추가금을 더하지 않음
        # 결정된 가격을 return
        return price

    # 잡힌 물고기를 결정하는 함수
    def catch_fish(self, fish_list, fish_food):
        if fish_food.name == "갯지렁이":
            # 갯지렁이 떡밥을 사용한 경우
            # 물고기 리스트에서 가중치를 fish.a_prob로 설정하여 3마리를 랜덤으로 선택
            fish_list = random.choices(fish_list, weights=[fish.a_prob for fish in fish_list], k=3)

        elif fish_food.name == "옥수수전분":
            # 옥수수전분 떡밥을 사용한 경우
            # 물고기 리스트에서 가중치를 fish.b_prob로 설정하여 3마리를 랜덤으로 선택
            fish_list = random.choices(fish_list, weights=[fish.b_prob for fish in fish_list], k=3)

        elif fish_food.name == "물고기찌":
            # 물고기찌 떡밥을 사용한 경우
            # 물고기 리스트에서 가중치를 fish.c_prob로 설정하여 3마리를 랜덤으로 선택
            fish_list = random.choices(fish_list, weights=[fish.c_prob for fish in fish_list], k=3)

        # 위에서 선택된 물고기 리스트에서 가중치를 fish.prob로 설정하여 1마리를 랜덤으로 선택
        fish = random.choices(fish_list, weights=[fish.prob for fish in fish_list], k=1)[0]
        # 선택된 물고기의 크기를 랜덤하게 설정
        size = random.randint(fish.min_size, fish.max_size)
        # 선택된 물고기의 가격을 결정 (추가금 포함)
        price = self.special_price(fish, size)
        return fish, size, price  # 잡힌 물고기의 종류, 크기, 가격을 결정하여 return




    # =========== 도감 창 GUI ============
    # 도감 창 구현 함수
    def show_fish_catalog(self, event):
        trophy_visible = False  # 트로피 노출 여부 초기화
        if self.catalog_visible or self.current_video != self.video1:  # 도감 창이 이미 열려 있는 경우 그리고 대기 상태인지 확인
            return
        self.catalog_window = Tk()  # 새로운 tkinter 창 생성
        self.catalog_window.title("물고기 도감")  # 상단 창 이름 설정
        catalog_canvas = Canvas(self.catalog_window, width=1280, height=720)  # 창 크기를 1280X720으로 설정
        catalog_canvas.pack()  # 캔버스를 화면에 배치
        # background 이미지 설정
        # ** 현재 tkinter 창이 하나 더 열려있는 상태(메인 화면)이기 때문에 master를 catalog_window로 설정해주지 않으면 에러가 발생함
        background_image = ImageTk.PhotoImage(Image.open("fishbook/background.png"), master=self.catalog_window)
        catalog_canvas.create_image(0, 0, anchor=NW, image=background_image)  # 좌표 0,0부터 background 이미지를 깔아줌
        caught_fish = self.fishbook_fish  # 도감 창에 출력할 물고기 종류를 fishbook_fish에서 받아옴

        # 도감 창 메인에 출력할 물고기 이미지 경로 설정, 마찬가지로 master를 catalog_window로 설정해줘야함
        fish_images = {
            "잉어": ImageTk.PhotoImage(Image.open("fishbook/carp.png"), master=self.catalog_window),
            "금붕어": ImageTk.PhotoImage(Image.open("fishbook/goldfish.png"), master=self.catalog_window),
            "툭눈금붕어": ImageTk.PhotoImage(Image.open("fishbook/telescope_goldfish.png"), master=self.catalog_window),
            "난주": ImageTk.PhotoImage(Image.open("fishbook/golden_bulldog_fish.png"), master=self.catalog_window),
            "송사리": ImageTk.PhotoImage(Image.open("fishbook/killifish.png"), master=self.catalog_window),
            "가재": ImageTk.PhotoImage(Image.open("fishbook/lobster.png"), master=self.catalog_window),
            "올챙이": ImageTk.PhotoImage(Image.open("fishbook/tadpole.png"), master=self.catalog_window),
            "가물치": ImageTk.PhotoImage(Image.open("fishbook/giant_snakehead.png"), master=self.catalog_window)
        }

        # 도감 창 상세 정보에 출력할 물고기 이미지 경로 설정, 마찬가지로 master를 catalog_window로 설정해줘야함
        fish_info_images = {
            "잉어": ImageTk.PhotoImage(Image.open("fishbook/carp_info.png"), master=self.catalog_window),
            "금붕어": ImageTk.PhotoImage(Image.open("fishbook/goldfish_info.png"), master=self.catalog_window),
            "툭눈금붕어": ImageTk.PhotoImage(Image.open("fishbook/telescope_goldfish_info.png"), master=self.catalog_window),
            "난주": ImageTk.PhotoImage(Image.open("fishbook/golden_bulldog_fish_info.png"), master=self.catalog_window),
            "송사리": ImageTk.PhotoImage(Image.open("fishbook/killifish_info.png"), master=self.catalog_window),
            "가재": ImageTk.PhotoImage(Image.open("fishbook/lobster_info.png"), master=self.catalog_window),
            "올챙이": ImageTk.PhotoImage(Image.open("fishbook/tadpole_info.png"), master=self.catalog_window),
            "가물치": ImageTk.PhotoImage(Image.open("fishbook/giant_snakehead_info.png"), master=self.catalog_window)
        }

        # trophy 말풍선 이미지와 업적 달성 시 노출되는 트로피 아이콘 이미지 경로 설정
        trophy_image = ImageTk.PhotoImage(Image.open("fishbook/trophy.png"), master=self.catalog_window)
        trophyicon_image = ImageTk.PhotoImage(Image.open("fishbook/trophyicon.png"), master=self.catalog_window)

        # caugh_fish에 해당하는 물고기가 있는지 확인하고, 만약 있다면 물고기마다 정해진 좌표에 배치한다.
        # 배치한 물고기를 클릭하면 fish_click 함수를 호출한다.
        if "잉어" in caught_fish:
            carp = catalog_canvas.create_image(100, 190, anchor=NW, image=fish_images["잉어"])
            catalog_canvas.tag_bind(carp, "<Button-1>", lambda event: fish_click(event, "잉어"))
        if "금붕어" in caught_fish:
            goldfish = catalog_canvas.create_image(370, 190, anchor=NW, image=fish_images["금붕어"])
            catalog_canvas.tag_bind(goldfish, "<Button-1>", lambda event: fish_click(event, "금붕어"))
        if "툭눈금붕어" in caught_fish:
            telescope_goldfish = catalog_canvas.create_image(645, 190, anchor=NW, image=fish_images["툭눈금붕어"])
            catalog_canvas.tag_bind(telescope_goldfish, "<Button-1>", lambda event: fish_click(event, "툭눈금붕어"))
        if "난주" in caught_fish:
            golden_bulldog_fish = catalog_canvas.create_image(922, 190, anchor=NW, image=fish_images["난주"])
            catalog_canvas.tag_bind(golden_bulldog_fish, "<Button-1>", lambda event: fish_click(event, "난주"))
        if "송사리" in caught_fish:
            killifish = catalog_canvas.create_image(100, 370, anchor=NW, image=fish_images["송사리"])
            catalog_canvas.tag_bind(killifish, "<Button-1>", lambda event: fish_click(event, "송사리"))
        if "가재" in caught_fish:
            lobster = catalog_canvas.create_image(370, 370, anchor=NW, image=fish_images["가재"])
            catalog_canvas.tag_bind(lobster, "<Button-1>", lambda event: fish_click(event, "가재"))
        if "올챙이" in caught_fish:
            tadpole = catalog_canvas.create_image(645, 370, anchor=NW, image=fish_images["올챙이"])
            catalog_canvas.tag_bind(tadpole, "<Button-1>", lambda event: fish_click(event, "올챙이"))
        if "가물치" in caught_fish:
            giant_snakehead = catalog_canvas.create_image(922, 370, anchor=NW, image=fish_images["가물치"])
            catalog_canvas.tag_bind(giant_snakehead, "<Button-1>", lambda event: fish_click(event, "가물치"))

        # 도감 메인 창 클릭 이벤트 핸들링
        def handle_catalog_click(event):
            # 도감 창이 열려있는 상태에서 도감 우측 하단 150, 100 좌표 클릭한 경우
            if self.catalog_visible and event.x >= self.catalog_window.winfo_width() - 150 and event.y >= self.catalog_window.winfo_height() - 100:
                # 도감을 닫는다
                self.close_fish_catalog(event)
            nonlocal trophy_visible
            # trophy_visible이 true인 경우
            if trophy_visible:
                # 트로피 이미지를 삭제한다
                catalog_canvas.delete(trophy)
                # trophy_visible를 False로 만들어준다
                trophy_visible = False

        # 물고기 상세 정보 창 구현
        def show_fish_info(fish):
            if self.info_window is not None:  # 다른 상세 정보 창이 이미 열려 있는 경우
                self.info_window.destroy()  # 해당 창을 닫는다
            if fish in fish_info_images:
                # fish_info_images에 해당 물고기에 대한 이미지가 있는 경우
                info_image = fish_info_images[fish]  # 해당 물고기에 대한 이미지를 가져옴
                self.info_window = Toplevel(self.catalog_window)  # 새로운 상세 정보 창을 생성
                self.info_window.title("물고기 상세정보")  # 상세 정보 창의 제목을 설정
                info_canvas = Canvas(self.info_window, width=1280, height=720)  # Canvas를 생성
                info_canvas.pack()  # Canvas를 화면에 배치
                info_canvas.create_image(0, 0, anchor=NW, image=info_image)  # 상세정보 이미지를 Canvas에 추가

            # 상세 정보 창 닫기
            def close_info_window(event):
                self.info_window.destroy()  # 상세정보 창을 닫음
                self.info_window = None  # 상세정보 창 변수 초기화

            # 상세 정보 창이 열려있다면
            if self.info_window is not None:
                # gui 창에서 x를 누르거나
                self.info_window.protocol("WM_DELETE_WINDOW", close_info_window)
                # 마우스 왼쪽 클릭이 들어오면 close_info_window를 호출
                self.info_window.bind("<Button-1>", close_info_window)

        # 도감 창 개별 물고기 클릭 시
        def fish_click(event, fish):
            show_fish_info(fish)  # 해당 물고기 상세 정보창 호출

        # 트로피 관련 로직 처리
        if len(caught_fish) == len(fish_images) and not self.trophy_displayed:
            # 잡은 물고기의 수가 전체 물고기의 수와 동일하고(개구리 제외), 트로피가 표시되지 않은 경우
            trophy = catalog_canvas.create_image(0, 0, anchor=NW, image=trophy_image)  # 트로피 말풍선 이미지를 도감 창에 출력
            trophy_visible = True  # 트로피가 현재 표시되고 있음을 나타내는 변수 true로 설정
            self.trophy_displayed = True  # 트로피가 표시되었음을 나타내는 변수를 true로 설정
        # 이미 트로피 말풍선이 표시 되었다면
        if self.trophy_displayed:
            # 정해진 위치에 트로피 아이콘 출력
            catalog_canvas.create_image(1080, 15, anchor=NW, image=trophyicon_image)

        # 도감 메인 창 관련 나머지 로직
        self.catalog_visible = True  # 도감 메인 창이 열려있음을 나타내는 변수 true로 설정
        catalog_canvas.bind('<Button-1>', handle_catalog_click)  # 왼쪽 마우스 클릭 이벤트 바인딩 (트로피 말풍선 클릭 처리 위해)
        self.catalog_window.protocol("WM_DELETE_WINDOW", lambda: self.close_fish_catalog(
            event=None))  # 도감 창에서 x 누를 때 close_fish_catalog 함수 호출.
        self.catalog_window.bind("b", self.close_fish_catalog)  # 도감 창에서 'b' 키를 누를 때 close_fish_catalog 함수 호출.
        self.catalog_window.bind("B", self.close_fish_catalog)  # 도감 창에서 'B' 키를 누를 때 close_fish_catalog 함수 호출.
        self.catalog_window.mainloop()  # 도감 창 이벤트 루프 실행

    # 도감 창 닫기
    def close_fish_catalog(self, event=None):
        if self.catalog_visible and self.catalog_window is not None:  # 도감 창이 열려 있는 경우
            self.catalog_window.destroy()  # 도감 창을 닫음
            self.catalog_window = None  # 도감 창 변수 초기화
            self.catalog_visible = False  # 도감 창 노출여부 변수 false
            self.start() # 다시 초기화면 호출



    # =========== 입력 이벤트 처리 ============
    # 입력 이벤트 바인딩(마우스 클릭, 키보드 입력)
    def bind_events(self):
        self.master.bind('<Button-1>', self.on_click)  # 마우스 왼쪽 클릭이 들어올 떄 on_click 함수 호출.
        self.master.bind('a', self.show_fish_catalog)  # 'a' 키를 누를 때 show_fish_catalog 함수 호출. (메인 창)
        self.master.bind('A', self.show_fish_catalog)  # 'A' 키를 누를 때 show_fish_catalog 함수 호출.
        self.master.bind('b', self.close_fish_catalog)  # 'b' 키를 누를 때 close_fish_catalog 함수 호출. (도감 창)
        self.master.bind('B', self.close_fish_catalog)  # 'B' 키를 누를 때 close_fish_catalog 함수 호출.
        self.master.bind('q', self.confirm_exit)  # 'q' 키를 누를 때 confirm_exit 함수 호출. (메인, 도감 창)
        self.master.bind('Q', self.confirm_exit)  # 'Q' 키를 누를 때 confirm_exit 함수 호출.
        self.master.protocol("WM_DELETE_WINDOW", self.exit_program)  # gui에서 x 키를 누를 때 exit_program 함수 호출.

    # 입력 이벤트 언바인딩(입력 금지)
    def unbind_events(self):
        self.master.unbind('<Button-1>')  # 마우스 왼쪽 클릭 이벤트 언바인딩
        self.master.unbind('a')  # 'a' 키 이벤트 언바인딩
        self.master.unbind('A')  # 'A' 키 이벤트 언바인딩

    # 낚시 성공 여부 판단
    # throw-catch 영상 마지막이 물고기가 찌를 무는 장면인데, 영상 마지막 몇 초간(사용자 설정) 클릭이 알맞게 들어오면 true를 반환하도록 한다.
    def success_check(self, video, seconds):
        # 마지막 클릭이 없는 경우 False를 반환
        if self.last_click is None:
            return False
        # total_length 변수에는 비디오의 전체 길이를 초 단위로 계산하여 저장
        # 비디오의 프레임 수(cv2.CAP_PROP_FRAME_COUNT)를 초당 프레임 수(cv2.CAP_PROP_FPS)로 나누어 계산
        total_length = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
        # current_position 변수에는 비디오의 현재 위치를 초 단위로 가져온다
        # 비디오의 현재 위치(cv2.CAP_PROP_POS_MSEC)를 밀리초 단위로 가져와서 1000으로 나누어 초 단위로 변환
        current_position = video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # 현재 위치
        # 마지막 클릭이 비디오의 마지막 N초 이내에 있었는지 확인
        # total_length - current_position이 seconds보다 작거나 같아야 함. 즉, 비디오의 남은 길이가 seconds 이하인지 확인.
        # last_click의 시간이 현재 시간으로부터 seconds 이내에 있어야 한다. 위의 조건들이 모두 충족되면 성공으로 판단하고 True를 반환
        return total_length - current_position <= seconds and self.last_click >= time.time() - seconds

    # 메인 창 클릭 이벤트 핸들러
    # 낚시 관련 이벤트는 이 곳에서 전부 처리
    def on_click(self, event):
        if not self.click_allowed:  # click_allowed가 False면 클릭을 받지 않는다
            return
        if self.catalog_visible:  # 도감 창이 열려 있는 경우에도 클릭을 받지 않는다
            return
        # 특정 좌표의 범위인지 확인
        # 좌측 상단 터치가 들어왔을 경우
        if event.x < 70 and event.y < 80:
            self.show_fish_catalog(event)  # 도감 화면 열기
        # 우측 하단 터치가 들어왔을 경우
        elif event.x >= 595 and event.y >= 370:
            # 떡밥 종류 변경
            self.select_next_fish_food()
        # 그 외의 경우 (낚시를 위해 터치했다고 판단)
        else:
            self.click_allowed = False  # 시간 계산을 위해 그 이후에 들어오는 클릭을 막음
            self.last_click = time.time()  # 마지막 클릭 시간 업데이트
            if self.current_video == self.video2:  # 동영상이 throw-catch인 경우
                # 낚시 성공 여부 확인 (마지막 3초 안에 입력이 들어왔는지)
                if self.success_check(self.video2, 3):
                    fish_list = self.create_fish_list(self.current_date.month)  # 성공했다면 물고기 리스트 생성
                    # 결정된 물고기 리스트와 떡밥을 이용해서 catch_fish를 호출해 물고기를 잡고, fish, fish_size, fish_price를 반환받는다
                    fish, fish_size, fish_price = self.catch_fish(fish_list,
                                                                  self.fish_food_list[self.fish_food_index])
                    self.caught_fish.append((fish.name, fish_size))  # 잡은 물고기의 이름과 크기를 리스트에 추가
                    fish_video = cv2.VideoCapture(
                        fish.video_file)  # fish.video_file 경로의 물고기 동영상 파일을 fish_video 변수에 담음
                    self.unbind_events()  # 입력 이벤트 언바인딩(입력 금지)
                    self.play_video(fish_video)  # 해당되는 물고기 동영상 재생
                    # 출력용 리스트를 따로 만든 이유는 caught_fish를 그대로 쓰면 동영상이 재생되기 전에 GUI에 반영되기 때문
                    self.fish_display_list.append((fish.name, fish_size))
                    self.total_money += fish_price  # 물고기 가격을 total_money에 더해준다
                else:
                    self.unbind_events()  # 입력 이벤트 언바인딩(입력 금지)
                    self.play_video(self.video3)  # 낚시 실패 동영상 ver1 재생

                self.bind_events()  # 입력 이벤트 바인딩
                self.current_date += relativedelta(months=1)  # 현재 시간 1달 증가시킴
                self.update_display()  # 디스플레이 업데이트
                self.save_user_data()  # 유저 데이터 저장
                FishingGUI.start(self)  # 다시 초기 화면(start_video)로 돌아가기 위해 start 함수 호출
            else:
                self.play_video(self.video2)  # throw-catch(낚싯대 던지기) 동영상 재생
        self.bind_events()  # 입력 이벤트 바인딩

        # throw-catch 동영상인 상태에서 입력이 안들어왔을 때 (물고기가 도망가는 부분 구현)
        if self.current_video == self.video2 and not self.success_check(self.video2, 3):
            self.unbind_events()  # 입력 이벤트 언바인딩(입력 금지)
            self.play_video(self.video4)  # 낚시 실패 동영상 ver2 재생
            self.current_date += relativedelta(months=1)  # 현재 시간 1달 증가시킴
            self.update_display()  # 디스플레이 업데이트
            self.save_user_data()  # 유저 데이터 저장
            self.bind_events()  # 입력 이벤트 바인딩
            FishingGUI.start(self)  # 다시 초기 화면(start_video)로 돌아가기 위해 start 함수 호출



    # =========== 디스플레이 업데이트 ============
    # 디스플레이 업데이트
    def update_display(self):
        # 날짜, 떡밥, 잡은 물고기, 돈 디스플레이 업데이트
        self.update_date_display()
        self.update_fishfood_display()
        self.update_fish_display()
        self.update_money_display()

    # 잡은 물고기 디스플레이
    def update_fish_display(self):
        # 기존 떡밥 표시 삭제
        if self.fish_display is not None:
            self.canvas.delete(self.fish_display)
        fish_name, fish_length = self.fish_display_list[-1]  # 물고기 이름과 길이를 받아온다
        fish_str = f'{fish_name}, {fish_length}cm'
        fish_font = font.Font(family="Verdana", size=9, weight="bold")  # 폰트 설정
        if fish_name != 0 and fish_length != 0:  # 빈 칸일때 예외처리, 문자 길이에 따른 좌표 조절
            if len(fish_str) == 7:
                self.fish_display = self.canvas.create_text(623, 123, text=fish_str, fill="white", anchor="nw",
                                                            font=fish_font)
            elif len(fish_str) == 8:
                self.fish_display = self.canvas.create_text(618, 123, text=fish_str, fill="white", anchor="nw",
                                                            font=fish_font)
            elif len(fish_str) == 9:
                self.fish_display = self.canvas.create_text(613, 123, text=fish_str, fill="white", anchor="nw",
                                                            font=fish_font)
            elif len(fish_str) == 10:
                self.fish_display = self.canvas.create_text(608, 123, text=fish_str, fill="white", anchor="nw",
                                                            font=fish_font)
            else:
                self.fish_display = self.canvas.create_text(603, 123, text=fish_str, fill="white", anchor="nw",
                                                            font=fish_font)
        else:
            self.fish_display = self.canvas.create_text(602, 123, text='잡은 물고기가 없다..', fill="white", anchor="nw",
                                                        font=font.Font(family="Verdana", size=8, weight="bold"))

    # 돈 디스플레이
    def update_money_display(self):
        # 기존 돈 표시 삭제
        if self.money_display is not None:
            self.canvas.delete(self.money_display)

        # 새 돈 표시 추가
        money_str = int(self.total_money)
        money_font = font.Font(family="Verdana", size=12, weight="bold")  # 폰트 설정
        # 정해진 위치에 텍스트 출력 / format을 이용해 세 자리마다 끊어줌 / 돈 자리수가 늘수록 좌표를 알맞게 조금씩 변경해줌
        if money_str <= 9:
            self.money_display = self.canvas.create_text(648, 58, text=money_str, fill="white", anchor="nw",
                                                         font=money_font)
        elif money_str <= 99:
            self.money_display = self.canvas.create_text(643, 58, text=money_str, fill="white", anchor="nw",
                                                         font=money_font)
        elif money_str <= 999:
            self.money_display = self.canvas.create_text(637, 58, text=money_str, fill="white", anchor="nw",
                                                         font=money_font)
        elif money_str <= 9999:
            self.money_display = self.canvas.create_text(630, 58, text=format(money_str, ','), fill="white",
                                                         anchor="nw", font=money_font)
        elif money_str <= 99999:
            self.money_display = self.canvas.create_text(624, 58, text=format(money_str, ','), fill="white",
                                                         anchor="nw", font=money_font)
        elif money_str <= 999999:
            self.money_display = self.canvas.create_text(618, 58, text=format(money_str, ','), fill="white",
                                                         anchor="nw", font=money_font)
        else:
            self.money_display = self.canvas.create_text(611, 58, text=format(money_str, ','), fill="white",
                                                         anchor="nw", font=money_font)

    # 떡밥 디스플레이
    def update_fishfood_display(self):
        # 기존 떡밥 표시 삭제
        if self.fishfood_display is not None:
            self.canvas.delete(self.fishfood_display)
        fishfood_str = self.fish_food_list[self.fish_food_index].name
        fishfood_font = font.Font(family="Verdana", size=12, weight="bold")  # 폰트 설정
        # 정해진 위치에 텍스트 출력 / 옥수수전분만 다섯 글자라 출력 시 약간의 좌표 변경이 필요함
        if fishfood_str == '옥수수전분':
            self.fishfood_display = self.canvas.create_text(616, 427, text=fishfood_str, fill="white", anchor="nw",
                                                            font=fishfood_font)
        else:
            self.fishfood_display = self.canvas.create_text(623, 427, text=fishfood_str, fill="white", anchor="nw",
                                                            font=fishfood_font)

    # 날짜 디스플레이
    def update_date_display(self):
        # 기존 날짜 표시 삭제
        if self.date_display is not None:
            self.canvas.delete(self.date_display)

        # 새 날짜 표시 추가
        date_str = self.current_date.strftime("%Y년\n  %m월")
        date_font = font.Font(family="Verdana", size=12, weight="bold")  # 폰트 설정
        # 정해진 위치에 텍스트 출력 (60, 600)
        self.date_display = self.canvas.create_text(43, 397, text=date_str, fill="white", anchor="nw", font=date_font)




    # =========== 비디오 재생 관련 ============
    # 비디오 파일 설정
    def setup_video(self):
        self.video1 = cv2.VideoCapture('video/start_video.mp4')  # 초기 동영상 파일
        self.video2 = cv2.VideoCapture('video/throw-catch.mp4')  # 던지기-입질 동영상 파일
        self.video3 = cv2.VideoCapture('video/catch-fail.mp4')  # 낚시 실패 동영상 파일 ver1 (낚싯대 걷기)
        self.video4 = cv2.VideoCapture('video/catch-fail2.mp4')  # 낚시 실패 동영상 파일 ver2 (물고기 놓치고, 낚싯대 걷기)
        self.video5 = cv2.VideoCapture('video/intro.mp4')  # 게임 인트로 동영상 파일
        self.video6 = cv2.VideoCapture('video/ending.mp4')  # 엔딩 동영상 파일

    # 동영상 재생 기능
    def play_video(self, video):
        self.imgtk = None  # 변환할 이미지를 보관할 곳
        self.click_allowed = True  # 클릭 허용을 true로 설정
        self.current_video = video  # 현재 재생되는 비디오는 current_video에 담기게 됨
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 비디오의 프레임 위치를 처음으로 설정
        fps = video.get(cv2.CAP_PROP_FPS)  # 비디오의 초당 프레임 수를 가져온다, 30fps
        while True:
            ret, frame = video.read()  # 비디오에서 프레임을 읽어옴
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 비디오의 프레임 위치를 처음으로 설정
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # 프레임의 컬러 스페이스를 BGR에서 RGBA로 변환
            frame = cv2.resize(frame, (720, 480))  # 프레임의 크기를 720, 480으로 조정
            img = Image.fromarray(frame)  # 프레임을 이미지로 변환한다
            if self.imgtk is None:  # 이미지가 아무것도 없는 경우(처음)
                imgtk = ImageTk.PhotoImage(image=img)  # 이미지를 Tkinter 라이브러리에서 사용할 수 있는 형식으로 변환
            else:  # 이미 이미지가 있는 경우
                imgtk.paste(img)  # 그 위에 덮어서 재생


            self.canvas.create_image(0, 0, image=imgtk, anchor=NW)  # 캔버스에 변환한 이미지를 추가한다
            if self.current_video != self.video5:  # 현재 비디오가 intro 영상이 아니라면
                # intro 영상에서는 돈, 떡밥, 날짜 정보가 나와서는 안되기 때문
                self.update_display()  # 디스플레이 업데이트
            # self.master.update_idletasks()  # GUI 업데이트
            self.canvas.update()  # 캔버스 업데이트
            # 프레임 처리 로직
            time.sleep(0.005)  # 위에서 설정한 프레임 딜레이 시간만큼 대기
            del frame  # 비디오 재생에 사용했던 frame 삭제
            del imgtk  # 비디오 재생에 사용했던 imgtk 삭제 (메모리 부하를 줄이기 위함)

            # 비디오가 start_video(초기 비디오) 인 상태에서 돈이 999999 벨 이상이고, 엔딩 동영상이 한번도 플레이 된 적 없다면
            if self.current_video == self.video1 and self.total_money >= 999999 and not self.ending_video_played:
                self.ending_video_played = True  # 엔딩 달성여부 True로 업데이트
                self.unbind_events()  # 입력 이벤트 언바인드 (입력 금지)
                self.play_video(self.video6)  # 엔딩 영상을 재생
                self.bind_events()  # 입력 이벤트 바인드
                break

    # =========== 게임 실행 ============
    # 게임 시작 메소드
    def start(self):
        # caught_fish에서 개구리를 제외한 물고기들의 종류를 추출하여 중복을 제거한 후, 리스트로 변환하여 fishbook_fish에 넣는다.
        # 도감 gui 구성시 미관 상 9개 칸으로 제작했는데, 현재 잡히는 물고기의 종류는 총 10가지이므로 하나를 제외해야한다.
        # 개구리와 올챙이는 동일한 개체이므로 도감에는 올챙이만 등장하는 것으로 결정했다.
        # start 함수에 넣은 이유 : 물고기를 잡고 로직 처리를 하게 되면 유저 데이터에서 개구리가 있는 상태로 낚시를 안하고 도감을 바로 열게 되면 에러가 발생한다.
        # 그래서 첫 시점부터 반영해주었다.
        self.fishbook_fish = list(set([fish[0] for fish in self.caught_fish if fish[0] != "개구리"]))
        self.update_display()  # 디스플레이 업데이트

        
        while True:
            self.play_video(self.video1)  # start_video 재생


# 동작 간 발생하는 error를 핸들링 하기 위해 try except 문 사용, 동작에는 문제없음
try:
    if __name__ == "__main__":
        root = Tk()  # tkinter 객체 생성(게임 메인화면)
        app = FishingGUI(root)  # 게임 전체 객체 생성
        app.show_initial_screen()  # 초기화면 호출
        root.mainloop()  # tkinter 이벤트 루프 실행
except Exception as e:
     pass