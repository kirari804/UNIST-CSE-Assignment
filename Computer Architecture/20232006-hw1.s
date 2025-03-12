.data # Data segment
prompt: .asciiz "The index for the Fibonacci sequence: " # Prompt for input
fib_result: .asciiz "Fibonacci number: " # Format for Fibonacci result
call_count: .asciiz "The number of fibonacci function calls: " # Format for call count
newline: .asciiz "\n" # Newline string
cnt:    .word 0 
 .text # Code segment
 .globl main # Entry point

main:

    # Print "The index for the Fibonacci sequence: "
    li $v0, 4 # syscall for print_string
    la $a0, prompt # Load address of prompt
    syscall

    # Read integer input (n)
    li $v0, 5 # syscall for read_int
    syscall
    move $a0, $v0 # Move input (n) to $a0 for fibonacci call


    jal fibonacci 

    move $t0, $v0 #move fibonacci function result to $t0

    #Print Fibonacci number: 
    li $v0, 4   #syscall for print_string           
    la $a0, fib_result   #load address of fib_result to $a0
    syscall

    move $a0, $t0  #move fibonacci function result to $a0        
    li $v0, 1 #syscall for print_int             
    syscall  

    #newline
    li $v0, 4  #syscall for print_string           
    la $a0, newline  #load address of new_line          
    syscall

    # Print The number of fibonacci function calls: 
    li $v0, 4   #syscall for print_string          
    la $a0, call_count   #load address of call_count  
    syscall

    #cnt
    la $t1, cnt  #load address of cnt         
    lw $a0, 0($t1)  #restore value of cnt into $a0       
    li $v0, 1  #syscall for print_int            
    syscall
    
    #newline
    li $v0, 4  #syscall for print_string           
    la $a0, newline  #load address of new_line      
    syscall

    

    # Exit program
    li $v0, 10 # syscall for exit
    syscall

fibonacci:
    addi $sp, $sp, -12 #allocate space on stack
    sw $ra, 8($sp) #store return address
    sw $t2, 4($sp) #store $t2
    sw $a0, 0($sp) #store argument of fibonacci function

    la $t1, cnt #load the address of cnt
    lw $t0, 0($t1) #load value of cnt to $t0
    addi $t0, $t0, 1  #cnt = cnt+1
    sw $t0, 0($t1) #store the updated cnt
    beq $a0, $zero, base_case_0  #if n=0, return 0
    li $t1, 1 #register $1 holds value 1
    beq $a0, $t1, base_case_1 # if n=1, return 1

    #Recursion:
    addi $a0, $a0, -1 #n = n-1
    jal fibonacci 
    move $t2, $v0 #save f(n-1) to register $t2
    lw $a0, 0($sp) #restore value of n
    addi $a0, $a0, -2 #n = n-2
    jal fibonacci
    add $v0, $v0, $t2 #f(n) = f(n-1)+f(n-2)


    lw $ra, 8($sp) #restore return address       
    lw $t2, 4($sp) #restore $2
    lw $a0, 0($sp) #restore argument of fibonacci function        
    addi $sp, $sp, 12  #deallocate space on stack   
    jr $ra #return control to caller

base_case_0:
    li $v0, 0 #return 0
    lw $ra, 8($sp) #restore return address         
    lw $t2, 4($sp) #restore $2
    lw $a0, 0($sp) #restore argument of fibonacci function         
    addi $sp, $sp, 12 #deallocate space on stack        
    jr $ra #return control to caller                         
 

base_case_1:
    li $v0, 1         
    lw $ra, 8($sp) #restore return address         
    lw $t2, 4($sp) #restore $2
    lw $a0, 0($sp) #restore argument of fibonacci function         
    addi $sp, $sp, 12 #deallocate space on stack 
    jr $ra #return control to caller 
