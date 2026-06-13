"""
Test cases for TyC code generation.
"""

from src.utils.nodes import *
from utils import CodeGenerator

# ! ## java -jar jasmin.jar *.j && java -noverify TyC
def test_001():
    source = """
    void main() {
        printString("Hello World");
    }
    """
    assert CodeGenerator().generate_and_run(source) == "Hello World"


def test_002():
    source = """
    void main() {
        printInt(42);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "42"


def test_003():
    source = """
    void main() {
        printFloat(3.14);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3.14"


def test_004():
    source = """
    void main() {
        int x = 10;
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10"


def test_005():
    source = """
    void main() {
        printInt(5 + 3);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "8"


def test_006():
    source = """
    void main() {
        printInt(6 * 7);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "42"


def test_007():
    source = """
    void main() {
        if (1 < 2)
            printString("yes");
        else
            printString("no");
    }
    """
    assert CodeGenerator().generate_and_run(source) == "yes"


def test_008():
    source = """
    void main() {
        int i = 0;
        while (i < 3) {
            printInt(i);
            i = i + 1;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "012"


def test_009():
    source = """
    int add(int a, int b) {
        return a + b;
    }

    void main() {
        printInt(add(20, 22));
    }
    """
    assert CodeGenerator().generate_and_run(source) == "42"


def test_010():
    source = """
    void main() {
        int x = 10;
        int y = 20;
        printInt(x + y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "30"

def test_011():
    source = """
    void main() {
        printFloat(1 + 1.2);
        printFloat(1.1 * 2);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2.22.2"

def test_012():
    source = """
    void main() {
        printInt(1 <= 1.2);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1"

def test_013():
    source = """
    int foo() {
        printInt(1);
        return 1;
    }
    void main() {
        printInt(1 && foo());
        printInt(1 || foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "111"

def test_014():
    source = """
    int foo() {
        printInt(1);
        return 1;
    }
    void main() {
        printInt(1 && foo());
        printInt(1 || foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "111"


def test_015():
    source = """
    void main() {
        printInt(!0);
        printInt(- - - 2);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1-2"

def test_016():
    source = """
    void main() {
        int a = 2;
        printInt(++a);
        printInt(a);
        printInt(-- a);
        printInt(a);        
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3322"

def test_017():
    source = """
    void main() {
        int a = 2;
        printInt(a++);
        printInt(a);
        printInt(a--);
        printInt(a);        
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2332"

def test_018():
    source = """
    void main() {
        int i = 0;
        while (i < 5) {
            i = i + 1;

            if (i == 2) {
                continue;
            }

            if (i == 4) {
                break;
            } else {
                printInt(i);
            }
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "13"


def test_019():
    source = """
    void main() {
        for(int i = 0; i <= 10; i++){
            printInt(i);
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234567891011"

def test_020():
    source = """
    void main() {
        int x = 3;
        switch (x) {
            case 1: printInt(1);
            case 3: printInt(3);
            case 5: printInt(5);
            default: printInt(7);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "357"

def test_021():
    source = """
    void main() {
        int x = 3;
        {
            int x = 2;
        }
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3"

def test_022():
    source = """
    void main() {
        int x = 5;
        switch (x) {
            case 1: printInt(1);
            case 3: printInt(3);
            case 5: int b = 2; printInt(b);
            default: b = 3; printInt(b);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "23"

def test_023():
    source = """
    struct Point {
        int x;
        int y;
    };
    void main(){
        Point p;
        p.x = 2;
        printInt(p.x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"

def test_024():
    source = """
    struct Point {
        int x;
        int y;
    };
    void main(){
        Point p;
        int a;
        a = p.y = 3;
        printInt(a);
        printInt(p.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "33"

def test_025():
    source = """
    void main(){
        printInt(readInt());
        printFloat(readFloat());
        printString(readString());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "22.2votien"

def test_026():
    source = """
    void main(){
        int a = 0;
        float b = 0.0;
        string c = "";
        printInt(a);
        printFloat(b);
        printString(c);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "00.0"

def test_027():
    source = """
    struct Point {
        int x;
        float y;
        string z;
    };
    void main(){
        Point p;
        printInt(p.x);
        printFloat(p.y);
        printString(p.z);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "00.0"

def test_028():
    source = """
    struct A {int x;};
    struct B {A a;};
    void main(){
        B p;
        printInt(p.a.x + 1);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1"

def test_029():
    source = """
    struct Point {
        int x;
        float y;
        string z ;
    };
    void main(){
        Point p = {1,2.2,"votien"};
        printInt(p.x);
        printFloat(p.y);
        printString(p.z);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "12.2votien"

def test_030():
    source = """
    void main(){
        auto a; auto b;
        {a = b = 1;}
        printInt(a + b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"

def test_031():
    source = """
foo(int a, int b) {return a + b;}
void main(){
    auto a = 0; auto b = 0;
    printInt(foo(a, b));
}
    """
    assert CodeGenerator().generate_and_run(source) == "0"


def test_032():
    source = """
int add(int x, int y) {
    return x + y;
}

int multiply(int x, int y) {
    return x * y;
}

void main() {
    auto a = readInt();
    auto b = readInt();
    
    auto sum = add(a, b);
    auto product = multiply(a, b);
    
    printInt(sum);
    printInt(product);
}
    """
    assert CodeGenerator().generate_and_run(source) == "44"

def test_033():
    source = """
void main() {
    auto n = 10;
    auto i = 0;
    
    while (i < n) {
        printInt(i);
        ++i;
    }
    
    for (auto j = 0; j < n; ++j) {
        if (j % 2 == 0) {
            printInt(j);
        }
    }
}
    """
    assert CodeGenerator().generate_and_run(source) == "012345678902468"


def test_034():
    source = """
void main() {
    // With auto and initialization
    auto x = readInt();
    auto y = readFloat();
    auto name = readString();
    
    // With auto without initialization
    auto sum;
    sum = x + y;              // sum: float (inferred from first usage - assignment)
    
    // With explicit type and initialization
    int count = 0;
    float total = 0.0;
    string greeting = "Hello, ";
    
    // With explicit type without initialization
    int i;
    float f;
    i = readInt();            // assignment to int
    f = readFloat();          // assignment to float
    
    printFloat(sum);
    printString(greeting);
    printString(name);
    
    // Note: String concatenation is NOT supported
    // This is because + operator applies to int or float, not string
}
    """
    assert CodeGenerator().generate_and_run(source) == "4.2Hello, votien"

def test_035():
    source = """
struct Point {
    int x;
    int y;
};

struct Person {
    string name;
    int age;
    float height;
};

void main() {
    // Struct variable declaration without initialization
    Point p1;
    p1.x = 10;
    p1.y = 20;
    
    // Struct variable declaration with initialization
    Point p2 = {30, 40};
    
    // Access and modify struct members
    printInt(p2.x);
    printInt(p2.y);
    
    // Struct assignment
    p1 = p2;  // Copy all members
    
    // Person struct usage
    Person person1 = {"John", 25, 1.75};
    printString(person1.name);
    printInt(person1.age);
    printFloat(person1.height);
    
    // Modify struct members
    person1.age = 26;
    person1.height = 1.76;
    
    // Using struct with auto
    auto p3 = p2;  // p3: Point (inferred from assignment)
    printInt(p3.x);
}
    """
    assert CodeGenerator().generate_and_run(source) == "3040John251.7530"

def test_036():
    source = """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

void main() {
    auto num = 10;
    auto result = factorial(num);
    printInt(result);
}
    """
    assert CodeGenerator().generate_and_run(source) == "3628800"

def test_037():
    source = """
    void main() {
        if (1)
            printString("yes");
        else
            printString("no");
    }
    """
    assert CodeGenerator().generate_and_run(source) == "yes"


def test_038():
    source = """
    void main() {
        if (0)
            printString("yes");
        else
            printString("no");
    }
    """
    assert CodeGenerator().generate_and_run(source) == "no"


def test_039():
    source = """
    void main() {
        int x = 5;
        if (x > 3)
            printInt(1);
        else
            printInt(0);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1"


def test_040():
    source = """
    void main() {
        int x = 2;
        if (x > 3)
            printInt(1);
        else
            printInt(0);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0"


def test_041():
    source = """
    void main() {
        int x = 10;
        if (x == 10)
            if (x > 5)
                printString("A");
            else
                printString("B");
        else
            printString("C");
    }
    """
    assert CodeGenerator().generate_and_run(source) == "A"

def test_042():
    source = """
    void main() {
        int x = 10;
        if (x == 10)
            if (x < 5)
                printString("A");
            else
                printString("B");
    }
    """
    assert CodeGenerator().generate_and_run(source) == "B"

def test_043():
    source = """
    void main() {
        int x = 10;
        if (x == 10) x = 1;
        else x = 2;
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1"

def test_044():
    source = """
    void main() {
        int x = 10;
        if (x != 10) x = 1;
        else x = 2;
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"


def test_045():
    source = """
    void main() {
        int x = 10;
        if (x == 10)
        {
            int x;
            x = 1;
        }
        else {
            int x;
            x = 2;
        }
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10"

def test_046():
    source = """
    void main() {
        int x = 10;
        if (x != 10)
        {
            int x;
            x = 1;
        }
        else {
            int x;
            x = 2;
        }
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10"

def test_047():
    source = """
    void main() {
        int i = 0;
        while (i < 5) {
            printInt(i);
            i = i + 1;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_048():
    source = """
    void main() {
        int i = 5;
        while (i > 0) {
            printInt(i);
            i = i - 1;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "54321"


def test_049():
    source = """
    void main() {
        int i = 0;
        while (i < 6) {
            i = i + 1;
            if (i == 3) continue;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "12456"


def test_050():
    source = """
    void main() {
        int i = 0;
        while (i < 10) {
            i = i + 1;
            if (i == 5) break;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1234"

def test_051():
    source = """
    void main() {
        int i = 1;
        while (i <= 3) {
            int j = 1;
            while (j <= 3) {
                printInt(i * j);
                j = j + 1;
            }
            i = i + 1;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "123246369"

def test_052():
    source = """
    void main() {
        int i = 0;
        while (i < 3) {
            int j = 0;
            while (j < 3) {
                j = j + 1;
                if (j == 2) continue;
                if (i == 2) break;
                printInt(i * 10 + j);
            }
            i = i + 1;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "131113"

def test_053():
    source = """
    void main() {
        int i = 0;
        while (i < 3) break;
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0"

def test_054():
    source = """
    void main() {
        for (int i = 0; i < 5; i++) {
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_055():
    source = """
    void main() {
        int i = 5;
        for (i = 5; i > 0; i--) {
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "54321"


def test_056():
    source = """
    void main() {
        for (int i = 0; i < 6; i++) {
            if (i == 3) continue;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01245"


def test_057():
    source = """
    void main() {
        for (int i = 0; i < 10; i++) {
            if (i == 5) break;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_058():
    source = """
    void main() {
        for (int i = 1; i <= 3; i++) {
            for (int j = 1; j <= 2; j++) {
                printInt(i * j);
            }
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "122436"


def test_059():
    source = """
    void main() {
        int i = 0;
        for (i = 0; i < 4; ++i) {
            printInt(i);
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_060():
    source = """
    void main() {
        for (int i = 0; i < 3; i++) {
            printInt(i);
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0123"

def test_061():
    source = """
    void main() {
        int i = 0;
        for (; i < 5; i++) {
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_062():
    source = """
    void main() {
        int i = 0;
        for (; i < 5; ++i) {
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_063():
    source = """
    void main() {
        int i = 0;
        for (i = 0; ; i++) {
            if (i == 5) break;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "01234"


def test_064():
    source = """
    void main() {
        int i = 0;
        for (; ; i++) {
            if (i == 4) break;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0123"


def test_065():
    source = """
    void main() {
        int i = 0;
        for (; i < 4;) {
            printInt(i);
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0123"


def test_066():
    source = """
    void main() {
        int i = 0;
        for (;;) {
            if (i == 4) break;
            printInt(i);
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0123"


def test_067():
    source = """
    void main() {
        int i = 0;
        for (; i < 5;) {
            if (i == 2) {
                i++;
                continue;
            }
            printInt(i);
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0134"


def test_068():
    source = """
    void main() {
        int i = 0;
        for (; ; ) {
            if (i == 3) break;
            printInt(i);
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "012"


def test_069():
    source = """
    void main() {
        int i = 0;
        for (; i < 3; ) {
            int j = 0;
            for (; j < 2; ) {
                printInt(i * 10 + j);
                j++;
            }
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0110112021"


def test_070():
    source = """
    void main() {
        int i = 0;
        for (; ; ) {
            printInt(i);
            if (i == 2) break;
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "012"


def test_071():
    source = """
    void main() {
        for (int i = 0; ; ) {
            printInt(i);
            if (i == 2) break;
            i++;
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0122"

def test_072():
    source = """
    void main() {
        for (int i = 0; ; i = 2) {
            printInt(i);
            if (i == 2) break;
            i++;
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "022"

def test_073():
    source = """
    void main() {
        int x = 2;
        switch (x) {
            case 1: printInt(1);
            case 2: printInt(2);
            case 3: printInt(3);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "23"


def test_074():
    source = """
    void main() {
        int x = 5;
        switch (x) {
            case 1: printInt(1);
            case 2: printInt(2);
            default: printInt(9);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "9"


def test_075():
    source = """
    void main() {
        int x = 1;
        switch (x) {
            case 1: printInt(1);
            case 2: printInt(2);
            case 3: printInt(3);
            default: printInt(4);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1234"


def test_076():
    source = """
    void main() {
        int x = 3;
        switch (x) {
            case 1: printInt(1); break;
            case 3: printInt(3); break;
            case 5: printInt(5);
            default: printInt(9);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3"


def test_077():
    source = """
    void main() {
        int x = 2;
        switch (x) {
            case 1: printInt(1);
            case 2:
                int a = 7;
                printInt(a);
            default:
                a = 9;
                printInt(a);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "79"


def test_078():
    source = """
    void main() {
        int x = 10;
        switch (x) {
            case 1: printInt(1);
            case 2: printInt(2);
            case 3: printInt(3);
        }
        printInt(8);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "8"


def test_079():
    source = """
    void main() {
        int x = 2;
        switch (x) {
            case 1: printInt(1);
            case 2:
                switch (1) {
                    case 1: printInt(9);
                }
            default: printInt(5);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "95"


def test_080():
    source = """
    void main() {
        int x = 4;
        switch (x) {
            case 1: printInt(1);
            case 2: printInt(2);
            case 4:
                printInt(4);
                break;
            default: printInt(9);
        }
        printInt(7);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "47"

def test_081():
    source = """
    void main() {
        int i = 0;
        while (i < 5) {
            i = i + 1;
            switch (i) {
                case 2: continue;
                case 4: break;
                default: printInt(i);
            }
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1133455"

def test_082():
    source = """
    void main() {
        int i = 0;
        while (i < 6) {
            i = i + 1;
            switch (i) {
                case 3: continue;
                case 5: break;
                default: printInt(i);
            }
            printInt(9);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "192949969"
def test_083():
    source = """
    void main() {
        int i = 0;
        while (i < 4) {
            i = i + 1;
            switch (i) {
                case 1:
                    printInt(1);
                    continue;
                case 3:
                    printInt(3);
                    break;
                default:
                    printInt(8);
            }
            printInt(9);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1893989"

def test_084():
    source = """
    void main() {
        int i = 2;
        switch (i) {
            default: int i = 3;
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"

def test_085():
    source = """
    void main() {
        int i = 2;
        switch (i) {
            case 2: int i = 3;
        }
        printInt(i);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"

def test_086():
    source = """
    void main() {
        int i = 0;
        while (1) {
            if (i == 3) break;
            printInt(i);
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "012"


def test_087():
    source = """
    void main() {
        int i = 0;
        while (i < 5) {
            i++;
            if (i == 3) continue;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1245"


def test_088():
    source = """
    void main() {
        int i = 0;
        while (i < 3) {
            int j = 0;
            while (j < 3) {
                if (j == 1) break;
                printInt(i);
                printInt(j);
                j++;
            }
            i++;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "001020"


def test_089():
    source = """
    void main() {
        for(int i=0;i<5;i++){
            if(i==2) continue;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "0134"


def test_090():
    source = """
    void main() {
        for(int i=0;i<5;i++){
            if(i==3) break;
            printInt(i);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "012"


def test_091():
    source = """
    void main() {
        int x = 2;
        switch(x){
            case 1: printInt(1); break;
            case 2: printInt(2); break;
            default: printInt(9);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"


def test_092():
    source = """
    void main() {
        int x = 2;
        switch(x){
            case 1: printInt(1);
            case 2: printInt(2);
            default: printInt(9);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "29"


def test_093():
    source = """
    int foo() {
        return 42;
    }

    void main() {
        printInt(foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "42"


def test_094():
    source = """
    float foo() {
        return 3.5;
    }

    void main() {
        printFloat(foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3.5"


def test_095():
    source = """
    string foo() {
        return "abc";
    }

    void main() {
        printString(foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "abc"


def test_096():
    source = """
    void main() {
        int x = 1;
        {
            int x = 2;
            printInt(x);
        }
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "21"


def test_097():
    source = """
    void main() {
        int a = 5;
        printInt(++a);
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "66"


def test_098():
    source = """
    void main() {
        int a = 5;
        printInt(a++);
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "56"


def test_099():
    source = """
    void main() {
        int a = 5;
        printInt(--a);
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "44"


def test_100():
    source = """
    void main() {
        int a = 5;
        printInt(a--);
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "54"

def test_101():
    source = """
    void main() {
        int a;
        a = 10;
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10"


def test_102():
    source = """
    void main() {
        int a = 1;
        {
            a = 5;
        }
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "5"


def test_103():
    source = """
    void main() {
        int a = 1;
        {
            int a = 2;
            a = 3;
            printInt(a);
        }
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "31"
    

def test_104():
    source = """
    void main() {
        int a = 1;
        int b;
        {
            b = a + 4;
        }
        printInt(b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "5"


def test_105():
    source = """
    void main() {
        int a = 1;
        {
            int b = 2;
            {
                int c = a + b;
                printInt(c);
            }
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3"

def test_106():
    source = """
    int foo() {
        return 42;
    }

    void main() {
        int a = foo();
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "42"


def test_107():
    source = """
    int add(int a, int b) {
        return a + b;
    }

    void main() {
        int x = add(10, 20);
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "30"


def test_108():
    source = """
    int square(int x) {
        return x * x;
    }

    int cube(int x) {
        return square(x) * x;
    }

    void main() {
        printInt(cube(3));
    }
    """
    assert CodeGenerator().generate_and_run(source) == "27"


def test_109():
    source = """
    int max(int a, int b) {
        if (a > b)
            return a;
        return b;
    }

    void main() {
        int m = max(7, 3);
        printInt(m);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "7"


def test_110():
    source = """
    int foo() {
        int a = 5;
        return a + 2;
    }

    void main() {
        int x;
        x = foo();
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "7"

def test_111():
    source = """
    int foo(int a, float b) {
        return a;
    }

    float bar(float x) {
        return x;
    }

    string baz(string s) {
        return s;
    }

    void main() {
        int x = 10;
        float y = 2.5;
        string z = "hi";

        printInt(foo(x, y));
        printFloat(bar(y));
        printString(baz(z));
    }
    """
    assert CodeGenerator().generate_and_run(source) == "102.5hi"

def test_112():
    source = """
    int foo() { printInt(2); return 1; }
    void main() {
        printInt(1 || foo());
        printInt(0 || foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "121"


def test_113():
    source = """
    int foo() { printInt(9); return 1; }
    void main() {
        printInt(0 || foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "91"


def test_114():
    source = """
    int foo() { printInt(7); return 1; }
    void main() {
        printInt(1 && foo());
        printInt(0 && foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "710"



def test_115():
    source = """
    int foo() { printInt(5); return 0; }
    int bar() { printInt(6); return 1; }

    void main() {
        printInt(foo() || bar());
        printInt(bar() && foo());
    }
    """
    assert CodeGenerator().generate_and_run(source) == "561650"

def test_116():
    source = """
    void main() {
        printInt(5 + 3);     // int + int
        printFloat(5 + 2.5); // int + float
        printFloat(2.5 + 5); // float + int
        printFloat(1.5 + 2.5); // float + float

        printInt(10 - 4);
        printFloat(10 - 3.5);
        printFloat(3.5 - 10);
        printFloat(5.5 - 2.5);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "87.57.54.066.5-6.53.0"

def test_117():
    source = """
    void main() {
        printInt(6 * 3);        // int * int
        printFloat(6 * 2.5);    // int * float
        printFloat(2.5 * 4);    // float * int
        printFloat(2.5 * 3.5);  // float * float

        printInt(20 / 4);
        printFloat(20 / 2.5);
        printFloat(7.5 / 3);
        printFloat(7.5 / 2.5);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1815.010.08.7558.02.53.0"

def test_118():
    source = """
    void main() {
        int a = 10;
        int b = 3;

        printInt(a + b);   
        printInt(a - b);  
        printInt(a * b);  
        printInt(a / b);  
        printInt(a % b);   

        if ((a + b) > (a * b)) {
            printInt(1);
        } else {
            printInt(0);
        }

        if ((a % b) == 1) {
            printInt(9);
        } else {
            printInt(8);
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "137303109"

def test_119():
    source = """
    void main() {
        int a = 5;
        int b = 3;
        float x = 5.0;
        float y = 3.0;

        // int vs int
        printInt(a < b);   
        printInt(a <= b);  
        printInt(a > b);   
        printInt(a >= b);  
        printInt(a == b);  
        printInt(a != b);  

        // float vs int (force i2f conversion)
        printInt(x < b);   
        printInt(x > b);   
        printInt(x == b);  

        // float vs float
        printInt(x <= y);  
        printInt(x >= y);  
        printInt(x != y);  

        // mixed reversed order
        printInt(b < x);   
        printInt(b > x);   
        printInt(b == x);  
    }
    """
    assert CodeGenerator().generate_and_run(source) == "001101010011100"

def test_120():
    source = """
    void main() {
        int a;
        int b;

        a = 5;
        b = a;

        printInt(a);   // 5
        printInt(b);   // 5

        a = a + 3;
        printInt(a);   // 8

        b = a = 10;
        printInt(a);   // 10
        printInt(b);   // 10

        float x;
        x = 2.5;
        x = x + 1.5;
        printFloat(x); // 4.0
    }
    """
    assert CodeGenerator().generate_and_run(source) == "55810104.0"

def test_121():
    source = """
    int add(int a, int b) {
        return a + b;
    }

    float mul(float x, float y) {
        return x * y;
    }

    int identity(int x) {
        return x;
    }

    void main() {
        int a = 10;
        int b = 5;

        float x = 2.5;
        float y = 4.0;

        printInt(add(a, b));        // 15
        printInt(add(1, add(2, 3))); // 6

        printFloat(mul(x, y));      // 10.0
        printFloat(mul(2.0, mul(1.5, 2.0))); // 6.0

        printInt(identity(add(3, 4))); // 7
    }
    """
    assert CodeGenerator().generate_and_run(source) == "15610.06.07"

def test_122():
    source = """
    void main() {
        int a = 5;
        int b = 10;

        printInt(a++);  // 5
        printInt(a);    // 6

        printInt(b--);  // 10
        printInt(b);    // 9

        int c = a++;
        printInt(c);    // 6
        printInt(a);    // 7

        int d = b--;
        printInt(d);    // 9
        printInt(b);    // 8
    }
    """
    assert CodeGenerator().generate_and_run(source) == "561096798"

def test_123():
    source = """
    void main() {
        int a = 5;

        printInt(++a);  // 6
        printInt(a);    // 6

        printInt(--a);  // 5
        printInt(a);    // 5

        printInt(+ + +a);   // 5
        printInt(- - -a);   // -5
    }
    """
    assert CodeGenerator().generate_and_run(source) == "66555-5"

def test_124():
    source = """
    void main() {
        int a = 0;
        int b = 1;

        printInt(!a);   // 1
        printInt(!b);   // 0

        ++a;
        --b;

        printInt(a);    // 1
        printInt(b);    // 0

        printInt(!b);   // 1
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10101"

def test_125():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p;
        p.x = 2;
        p.y = 3;

        printInt(p.x);
        printInt(p.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "23"


def test_126():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p = {5, 7};
        printInt(p.x);
        printInt(p.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "57"


def test_127():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p1 = {1, 2};
        Point p2 = p1;

        printInt(p2.x);
        printInt(p2.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "12"


def test_128():
    source = """
    struct A { int x; };
    struct B { A a; };

    void main() {
        B b;
        b.a.x = 9;
        printInt(b.a.x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "9"


def test_129():
    source = """
    struct Point {
        int x;
        float y;
        string z;
    };

    void main() {
        Point p = {3, 2.5, "ok"};

        printInt(p.x);
        printFloat(p.y);
        printString(p.z);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "32.5ok"


def test_130():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p;
        p.x = 10;
        p.y = p.x + 5;

        printInt(p.x);
        printInt(p.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1015"

def test_131():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p1;
        Point p2;

        p2.x = 10;
        p2.y = 20;

        p1 = p2;   // copy struct

        p2.x = 99;
        p2.y = 88;

        printInt(p1.x);
        printInt(p1.y);
        printInt(p2.x);
        printInt(p2.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10209988"

def test_132():
    source = """
    struct Point {
        int x;
        int y;
    };

    Point makePoint(int a, int b) {
        Point p;
        p.x = a;
        p.y = b;
        return p;
    }

    void main() {
        Point p = makePoint(3, 7);

        printInt(p.x);
        printInt(p.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "37"

def test_133():
    source = """
    struct Point {
        int x;
        int y;
    };

    int sum(Point p) {
        return p.x + p.y;
    }

    void printPoint(Point p) {
        printInt(p.x);
        printInt(p.y);
    }

    void main() {
        Point p;
        p.x = 4;
        p.y = 6;

        printPoint(p);
        printInt(sum(p));
    }
    """
    assert CodeGenerator().generate_and_run(source) == "4610"

def test_134():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point a;
        Point b;

        a = b = {1, 2};

        printInt(a.x);
        printInt(a.y);
        printInt(b.x);
        printInt(b.y);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1212"

def test_135():
    source = """
    struct A { int x; };
    struct B { A a; };
    struct C { B b; };
    struct D { C c; };

    void main() {
        D d1;
        D d2;

        d2.c.b.a.x = 10;

        d1 = d2 = d2;

        printInt(d1.c.b.a.x);
        printInt(d2.c.b.a.x);

        d2.c.b.a.x = d2.c.b.a.x + d2.c.b.a.x - 10 + 10;

        printInt(d1.c.b.a.x);
        printInt(d2.c.b.a.x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10101020"

def test_136():
    source = """
    void main() {
        auto a = 10;
        auto b = 20;
        printInt(a + b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "30"


def test_137():
    source = """
    void main() {
        auto a = 1;
        {
            auto a = 5;
            printInt(a);
        }
        printInt(a);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "51"


def test_138():
    source = """
    void main() {
        auto a;
        a = 3;
        auto b = a + 2;
        printInt(b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "5"


def test_139():
    source = """
    void main() {
        auto i = 0;
        while (i < 3) {
            printInt(i);
            i = i + 1;
        }
    }
    """
    assert CodeGenerator().generate_and_run(source) == "012"


def test_140():
    source = """
    int add(int x, int y) { return x + y; }

    void main() {
        auto a = add(10, 20);
        auto b = add(a, 5);
        printInt(b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "35"

def test_141():
    source = """
    foo(int a, int b) { return a + b; }

    void main() {
        auto x = foo(10, 20);
        printInt(x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "30"

def test_142():
    source = """
    bar(int x) { return x * 2; }

    void main() {
        auto a = bar(5);
        auto b = bar(a + 1);
        printInt(a);
        printInt(b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "1022"

def test_143():
    source = """
    int add(int a, int b) { return a + b; }

    void main() {
        auto a = add(5, 10);
        auto b = add(a, 20);
        auto c = add(b, a);
        printInt(c);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "50"


def test_144():
    source = """
    foo(int x) { return x * x; }

    void main() {
        auto a = foo(2);
        auto b = foo(a + 1);
        auto c = foo(b - 1);
        printInt(c);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "576"


def test_145():
    source = """
    void main() {
        auto a = 1;
        auto b = 2;
        auto c = a + b;

        {
            auto a = c + 1;
            printInt(a);
        }

        printInt(c);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "43"


def test_146():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p;
        p.x = 10;
        p.y = 20;

        auto a = p.x + p.y;
        auto b = a + p.x;

        printInt(b);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "40"


def test_147():
    source = """
    bar(int x) { return x * 2; }

    void main() {
        auto i = 0;
        auto sum = 0;

        while (i < 5) {
            sum = sum + bar(i);
            i = i + 1;
        }

        printInt(sum);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "20"


def test_148():
    source = """
    bar(int x) { return x * 2; }

    void main() {
        auto a = bar(1);
        auto b = bar(a);
        auto c = bar(b);
        auto d = bar(c);

        printInt(d);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "16"


def test_149():
    source = """
    int f(int x) { return x + 1; }

    void main() {
        auto a = f(1);
        auto b = f(f(a));
        auto c = f(f(f(b)));

        printInt(c);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "7"


def test_150():
    source = """
    foo(int x) { return x * 3; }

    void main() {
        auto a = foo(1);
        auto b = foo(foo(1));
        auto c = foo(foo(foo(1)));

        printInt(a);
        printInt(b);
        printInt(c);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "3927"


def test_151():
    source = """
    struct Point {
        int x;
        int y;
        int c;
        int d;
    };
    void main(){
        Point p;
        p.d = 2;
        Point p1 = p;
        p1.d = 3;
        printInt(p.d);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"

def test_152():
    source = """
    struct Point {
        int x;
        int y;
    };

    struct Line {
        Point start;
        Point end;
    };

    void main(){
        Line l1;

        l1.start.x = 10;
        l1.end.x = 20;

        Line l2 = l1;

        l2.start.x = 99;
        l2.end.x = 88;

        printInt(l1.start.x);
        printInt(l1.end.x);
    }
    """

    assert CodeGenerator().generate_and_run(source) == "1020"

def test_153():
    source = """
    struct Point {
        int x;
    };
    void main(){
        Point p;
        p.x = 2;
        Point p1;
        p1 = p;
        p1.x = 3;
        printInt(p.x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "2"

def test_154():
    source = """
    struct Point {
        int x;
    };

    void change(Point p){
        p.x = 99;
    }

    void main(){
        Point a;
        a.x = 10;

        change(a);

        printInt(a.x);
    }
    """
    assert CodeGenerator().generate_and_run(source) == "10"

def test_155():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main(){
        Point p1; Point p2; Point p3;
        p1.x = 1;
        p2 = p3 = p1;
        p1.x = 2;

        printInt(p1.x);
        printInt(p2.x);
        printInt(p3.x);    
    }
    """

    assert CodeGenerator().generate_and_run(source) == "211"


def test_156():
    source = """
    struct Point {
        int x;
        int y;
    };

    struct Rect {
        Point p;
    };

    void main() {
        Rect r1;
        Rect r2;

        r1.p.x = 1;
        r2 = r1;
        r1.p.x = 10;

        printInt(r1.p.x);
        printInt(r2.p.x);
    }
    """

    assert CodeGenerator().generate_and_run(source) == "101"

def test_157():
    source = """
    struct Point {
        int x;
    };

    struct Rect {
        Point p;
    };

    struct Box {
        Rect r;
    };

    void main() {
        Box b1;
        Box b2;

        b1.r.p.x = 1;

        b2 = b1;

        b1.r.p.x = 10;

        printInt(b1.r.p.x);
        printInt(b2.r.p.x);
    }
    """

    assert CodeGenerator().generate_and_run(source) == "101"

def test_158():
    source = """
    struct Point {
        int x;
    };

    struct Rect {
        Point p;
    };

    struct Box {
        Rect r;
    };

    struct Container {
        Box b;
    };

    void main() {
        Container c1;
        Container c2;

        c1.b.r.p.x = 1;

        c2 = c1;

        c1.b.r.p.x = 10;

        printInt(c1.b.r.p.x);
        printInt(c2.b.r.p.x);
    }
    """

    # shallow copy => 1010
    assert CodeGenerator().generate_and_run(source) == "101"

def test_159():
    source = """
    struct A { int x; };

    void main() {
        A a1; A a2;
        a1.x = 1;
        a2 = a1 = a1;
        a1.x = 2;    
        printInt(a2.x);
      printInt(a1.x);

    }
    """
    assert CodeGenerator().generate_and_run(source) == "12"

def test_160():
    source = """
    struct A { int x; };

    void main() {
        A a1;
        a1.x = 1;
        A a2 = a1 = a1;
        a1.x = 2;    
        printInt(a2.x);
      printInt(a1.x);

    }
    """
    assert CodeGenerator().generate_and_run(source) == "12"

