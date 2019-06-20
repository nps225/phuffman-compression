#Nikhil Sheth
#1577698

from Queue import PriorityQueue
import struct
import sys

#additional classes

#Leaf Class -- serves as the trees leaves -- allows for easier traversal
class Leaf:
    def __init__(self, char, count):
        self.char = char
        self.count = count

    def getChar(self):#returns the character
        return self.char

    def getCount(self):#returns the count
        return self.count

    def compare(self,other):#serves to compare two leaves/trees
        if self.count < other.count:
            return 1
        elif self.count > other.count:
            return -1
        elif self.char < other.char:
            return 1
        else:
            return -1

    def isLeaf(self):#if its a leaf
        return True

    def inorder1(self,s,l):#in order tree traversal -- returns the leaf itself
        if not s == None:
            return (self.getChar(),self.getCount(),s)

    def postorder(self,l):#post order tree traversal -- used for tree compression
        return self;#not going to do anything


class Tree(Leaf):#subclass of Leaf
    #Tree class takes on left leaf character and sum of left and right count
    def __init__(self, left, right):#stores left and right leaf
        self.left = left
        self.right = right
        self.char = self.left.getChar()
        self.count = self.left.getCount() + self.right.getCount()


    #two inorder traversals since I wanted to return a list of the entire tree
    def inorder(self,s,l):#in order traversal for first iteration
        if not self.left == None:
            b = s + "0"
            l.append(self.left.inorder1(b,l))
        if not self.right == None:
            c = s + "1"
            l.append(self.right.inorder1(c,l))
        l[:] = [x for x in l if x != None]
        return l


    def inorder1(self,s,l):#in order traversal for iterations above 1
        if not self.left == None:
            b = s + "0"
            l.append(self.left.inorder1(b,l))
        if not self.right == None:
            c = s + "1"
            l.append(self.right.inorder1(c,l))

    def postorder(self,l):#postorder traversal returns list of leafs
        if not self.left == None:
            l.append(self.left.postorder(l))
        if not self.right == None:
            l.append(self.right.postorder(l))
        l.append(self)
        return l


    def isLeaf(self):#if it is a leaf = false
        return False

    def isTree(self):#if it is a tree = true
        return True

#Decode Function
def decode(filename,output):#takes in input file and output file names
    #first lets get an iteratable string that I may iterate over freely
    with open(filename,"r+b") as f:#read the input file
         myArr = bytearray(f.read())#stores all binary in array

    f = open(output,"w+")#open up the output file for reading

    s = "" #hold all the binary info for the file

    #loop will put all the binary bits in string format and place in String s
    for i in myArr:
        s = s + '{0:08b}'.format(i)

    #now read s one by one and produce the output
    index = 0 # represent our location in the String s
    stack = []#will be our stack that helps us reassemble the huffman tree
    root = None#after while loop will return root

    #reassemble the tree
    while True:
        if s[index] == "0":#if we found a leaf
            index += 1
            if s[index:index + 9] == "000000001":#if it is EOF - 9 bits
                stack.insert(0,Leaf(256,0))
                index += 9
            elif s[index:index + 9] == "000000000":#if it is 0 - 9 bits
                stack.insert(0,Leaf(0,0))
                index += 9
            else:#if it is anything push it on the stack - 8 bits
                stack.insert(0,Leaf(int(s[index:index + 8],2),0))
                index += 8
        else:#if the value is 1 -- therefore assemble a new trees
            index += 1
            #first pop the first element of the stack
            root = stack.pop(0)#note --- is our right leaf of the tree
            #if the stack is empty our tree is assembled
            if len(stack) == 0:
                break
            #if not empty stack -- pop next element off
            left = stack.pop(0)
            #create a new tree from previous elements and push them back on
            #the stack
            stack.insert(0,Tree(left,root))

    #end result: root now holds our huffman tree

    s = s[index:]#the rest of the file we have to write

    #now iterate through my file
    index = 0#incrementor through the String s
    location = root#our location that we are at in the our tree

    #Method: I will read bit by bit and iterate through my tree in parallel with
    #with my file and once I hit a leaf I will print the character to my output
    #file, and then continue doing this process till I hit the eof character
    #where I will close and flush my file

    while True:
        if s[index] == "0":#go left in our tree
            location = location.left
        else:#go right in our leaf
            location = location.right
        if location.isLeaf():#if it is a leaf
            if location.getChar() == 256:#if it is eof
                #stop writing in our file
                f.flush()
                f.close()
                break
            else:#if it is anything but eof
                f.write(chr(location.getChar()))#write out character to output
            location = root#reset our location to the root of the tree
        #go to next bit in string
        index += 1

#Encode function
def encode(filename,output):
    #first generate our freq table
    freqtable = constructFreq(filename)
    #now place it into a priority queue
    priority = constructPQ(freqtable)
    #remake it as a bunch of leaves -- allows iterating through the tree to be easier
    leafPriority = constructLeafPQ(priority)
    root = constructTree(leafPriority)#takes in priority queue /stack of leaves
    encodedTable = root.inorder("",[])#serve as our encoded table
    #write our tree to the file as well as the file itself to output
    writeToFile(root,filename,output)

#write the information to the file
def writeToFile(root,filename,output):
    count = 0#helper counter -- counted the number of bits I was using
    nf = open(output,"w+b");
    f = open(filename,"r+b");
    #first write the huffman tree
    l = root.postorder([])
    l[:] = [x for x in l if type(x) != list]
    s = ""
    for node in l:#iterate through the posttraversal list
        if node.isLeaf():
            s = s + "0"
            count = count + 1
            if node.getChar() == 0 or node.getChar() == 256:
                    s = s + '{:08b}'.format(0)
                    count = count + 8
                    if node.getChar() == 256:
                        s = s + "1"
                        count = count + 1
                    else:
                        s = s + "0"
                        count = count + 1
            else:
                s = s + '{:08b}'.format(node.getChar())
                count = count + 8
        else:
            s = s + "1"
            count = count + 1
    s = s + "1"
    count = count + 1
    #write the actual file
    l = root.inorder("",[]);
    counter = 0
    with open(filename) as f:
        while True:
            counter = counter + 1
            c = f.read(1)
            if not c:
                s = s + findCharPath(l,256)
                break
            s = s + findCharPath(l,ord(c))

    #now write our binary string to the actual file
    if not len(s)%8 == 0:
        for i in range(0,8-len(s)%8):
            s = s + "0"
            count = count + 1

    inc = 0
    while inc < len(s)/8:
        binary = s[inc * 8:((inc + 1)*8)]
        a = chr(int(binary,2))
        nf.write(a)
        inc = inc + 1

#generate an array of 256
def generateArray():
    l = []
    for i in range(0,257):
        l.append(0)
    return l

#generates the frequency table
def constructFreq(filename):
    d = generateArray();#generates 256 array size

    with open(filename) as f:
        while True:#iterate through file recording the chacters in the array
            c = f.read(1)
            if not c:
                #end of file condition
                break
            d[ord(c)] = d[ord(c)] + 1
        d[256] = 1 #assign end of file a value don't forget to add this back
    return d

#generates the priority queue
def constructPQ(freqtable):
    s = []
    for i in range(0,257):
        if not freqtable[i] == 0:
            s.append((freqtable[i],i));
    return sorted(s, key=lambda tup: (tup[0],tup[1]) );

#makes a priority queue based as a bunch of leaves
def constructLeafPQ(priority):
    temp = []
    while not len(priority) == 0:
        leaf = priority.pop()#(count, char)
        temp.insert(0,Leaf(leaf[1],leaf[0]))
    return temp

#find the characters complimenting encoding in the list
def findCharPath(encodedTable,c):
    for (i,j,k) in encodedTable:
        if c == i:
            return k

#constructs a tree based off the priority queue
def constructTree(priority):
    while len(priority) > 1:
        #print priority
        leftLeaf = priority.pop(0)
        rightLeaf = priority.pop(0)
        root = Tree(leftLeaf,rightLeaf)
        #sort the priority back into place
        placed = False
        for i in range(0,len(priority)):
            #print chr(priority[i].getChar())
            if priority[i].compare(root) < 0 and not placed:
                placed = True
                priority.insert(i,root)
                break;
        if not placed:
            priority.append(root)
    return root

#handles user inputs
def main(argv):
    if argv[0] == "encode":
        #call encode
        encode(argv[1],argv[2])
    else:
        #call decode
        decode(argv[1],argv[2])


if __name__ == "__main__":
   main(sys.argv[1:])