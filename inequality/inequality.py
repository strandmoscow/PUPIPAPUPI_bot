import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from sympy import Symbol, latex
from sympy.solvers.inequalities import solve_univariate_inequality
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

INEQ_TYPE, GROUP_NUMBER, STUDENT_NUMBER = range(3)
ineq_dict = {}


async def inequality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["f(x)>0", "f(x)<0", "f(x)≥0", "f(x)≤0"]]

    await update.message.reply_text(
        "Тебе дано следующее задание, я помогу его тебе решить."
    )

    await update.message.reply_photo(open("inequality/ineqality_question.png", "rb"))

    await update.message.reply_text(
        "Выбери тип уравнения",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Inequality type"
        ),
    )

    return INEQ_TYPE


async def group_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    ineq_type = update.message.text
    if ineq_type == "f(x)>0":
        ineq_dict["type"] = 0
    elif ineq_type == "f(x)<0":
        ineq_dict["type"] = 1
    elif ineq_type == "f(x)≥0":
        ineq_dict["type"] = 2
    else:
        ineq_dict["type"] = 3
    logger.info("Type of inequality of %s: %s(%s)", user.first_name, update.message.text, ineq_dict["type"])

    await update.message.reply_text(
        f'Окей, вид уравнения выбран: {ineq_type}.',
        reply_markup=ReplyKeyboardRemove(),
    )

    await update.message.reply_text(
        "Напиши номер своей группы числом",
    )

    return GROUP_NUMBER


async def student_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    ineq_dict["group"] = update.message.text
    logger.info("Group of %s: %s", user.first_name, ineq_dict["group"])

    await update.message.reply_text(
        f'Хорошо, ты из группы {ineq_dict["group"]}.',
    )

    await update.message.reply_text(
        'Напиши твой номер по списку',
    )

    return STUDENT_NUMBER


def f(x, a, b, c, d, m, n):
    return (((x - a)**(n+1)) * ((x + b)**m)) / (((x + c)**n) * ((x - d)**(m+1)))


async def solution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    ineq_dict["number"] = update.message.text
    logger.info("List number of %s: %s", user.first_name, ineq_dict["number"])

    await update.message.reply_text(
        f'Так, твой номер в списке группы {ineq_dict["number"]}, считаю ответ',
    )

    n = int(ineq_dict["number"])
    m = int(ineq_dict["group"])
    a = m
    b = n
    c = m + n
    d = n - m
    x = Symbol('x', real=True)

    if ineq_dict["type"] == 0:
        tex = f'$\\frac{{ ( x - {a} )^{{ {n + 1} }} \\cdot (x + {b})^{{ {m} }} }}{{ (x + {{ {c} }})^{{ {n} }} \\cdot (x - {{ {d} }})^{{ {m + 1} }} }} > 0$'
    if ineq_dict["type"] == 1:
        tex = f'$\\frac{{ ( x - {a} )^{{ {n + 1} }} \\cdot (x + {b})^{{ {m} }} }}{{ (x + {{ {c} }})^{{ {n} }} \\cdot (x - {{ {d} }})^{{ {m + 1} }} }} < 0$'
    if ineq_dict["type"] == 2:
        tex = f'$\\frac{{ ( x - {a} )^{{ {n + 1} }} \\cdot (x + {b})^{{ {m} }} }}{{ (x + {{ {c} }})^{{ {n} }} \\cdot (x - {{ {d} }})^{{ {m + 1} }} }} \geqslant 0$'
    if ineq_dict["type"] == 3:
        tex = f'$\\frac{{ ( x - {a} )^{{ {n + 1} }} \\cdot (x + {b})^{{ {m} }} }}{{ (x + {{ {c} }})^{{ {n} }} \\cdot (x - {{ {d} }})^{{ {m + 1} }} }} \leqslant 0$'

    ### Создание области отрисовки
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    ### Отрисовка формулы
    t = ax.text(0.5, 0.5, tex,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=20, color='black')

    ### Определение размеров формулы
    ax.figure.canvas.draw()
    bbox = t.get_window_extent()

    # Установка размеров области отрисовки
    fig.set_size_inches(bbox.width / 80, bbox.height / 80)  # dpi=80

    ### Отрисовка или сохранение формулы в файл
    # plt.show()
    # plt.savefig('test.svg')
    plt.savefig('inequality/test.png', dpi=300)

    await update.message.reply_text(
        "Уравенение будет выглядеть так:"
    )

    await update.message.reply_photo(open("inequality/test.png", "rb"))

    sol = 0
    if ineq_dict["type"] == 0:
        sol = solve_univariate_inequality(f(x, a, b, c, d, m, n) > 0, x, relational=False)
    if ineq_dict["type"] == 1:
        sol = solve_univariate_inequality(f(x, a, b, c, d, m, n) < 0, x, relational=False)
    if ineq_dict["type"] == 2:
        sol = solve_univariate_inequality(f(x, a, b, c, d, m, n) >= 0, x, relational=False)
    if ineq_dict["type"] == 3:
        sol = solve_univariate_inequality(f(x, a, b, c, d, m, n) <= 0, x, relational=False)

    ### Создание области отрисовки
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    ### Отрисовка формулы
    t = ax.text(0.5, 0.5, '$' + latex(sol) + '$',
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=20, color='black')

    ### Определение размеров формулы
    ax.figure.canvas.draw()
    bbox = t.get_window_extent()

    # Установка размеров области отрисовки
    fig.set_size_inches(bbox.width / 80, bbox.height / 80)  # dpi=80

    ### Отрисовка или сохранение формулы в файл
    # plt.show()
    # plt.savefig('test.svg')
    plt.savefig('inequality/solution.png', dpi=300)

    await update.message.reply_text(
        "Решение"
    )

    await update.message.reply_photo(open("inequality/solution.png", "rb"))

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Ну как хочешь...", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

inequality_handler = ConversationHandler(
    entry_points=[CommandHandler("inequality", inequality)],
    states={
        INEQ_TYPE: [MessageHandler(filters.Regex("^f\(x\)>0|f\(x\)<0|f\(x\)≥0|f\(x\)≤0$"), group_number)],
        GROUP_NUMBER: [MessageHandler(filters.Regex("^[0-9]+"), student_number)],
        STUDENT_NUMBER: [MessageHandler(filters.Regex("^[0-9]+"), solution)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
