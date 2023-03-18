import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
import random

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you assign them
        Return: a tuple of a dictionary and a bool. The dictionary contains all MODIFIED variables, mapped to their MODIFIED domain.
                The bool is true if assignment is consistent, false otherwise.
    """
    def forwardChecking ( self ):
        var_domain={}
        for var in self.network.getVariables():
            assignedVal=var.getAssignment()
            if assignedVal:
                for neighbor in self.network.getNeighborsOfVariable(var):
                    if neighbor.getDomain().contains(assignedVal):
                        self.trail.push(neighbor)
                        neighbor.removeValueFromDomain(assignedVal)
                        domain=neighbor.getDomain()
                        if domain.isEmpty():
                            return (var_domain, False)
                        var_domain[neighbor]=domain
                            
                        
        return (var_domain, self.network.isConsistent())

    # =================================================================
	# Arc Consistency
	# =================================================================
    def arcConsistency( self ):
        assignedVars = []
        for c in self.network.constraints:
            for v in c.vars:
                if v.isAssigned():
                    assignedVars.append(v)
        while len(assignedVars) != 0:
            av = assignedVars.pop(0)
            for neighbor in self.network.getNeighborsOfVariable(av):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(av.getAssignment()):
                    neighbor.removeValueFromDomain(av.getAssignment())
                    if neighbor.domain.size() == 1:
                        neighbor.assignValue(neighbor.domain.values[0])
                        assignedVars.append(neighbor)

    
    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you assign them
        Return: a pair of a dictionary and a bool. The dictionary contains all variables 
		        that were ASSIGNED during the whole NorvigCheck propagation, and mapped to the values that they were assigned.
                The bool is true if assignment is consistent, false otherwise.
    """
    def norvigCheck ( self ):
        assignedVar={}
        for var in self.network.getVariables():
            assignedVal=var.getAssignment()
            if assignedVal:
                for neighbor in self.network.getNeighborsOfVariable(var):
                    if neighbor.getDomain().contains(assignedVal):
                        self.trail.push(neighbor)
                        neighbor.removeValueFromDomain(assignedVal)
                        domain=neighbor.getDomain()
                        if domain.isEmpty():
                            return (assignedVar, False)
                        
                        if domain.size() == 1:
                            value=domain.values[0]
                            neighbor.assignValue(value)
                            assignedVar[neighbor]=value
                            

        for unit in self.network.getConstraints(): 
            counter=dict()
            length=0
            
            for var in set(unit.vars):
                for val in set(var.getValues()):
                    if val not in counter:
                        counter[val]=[1,var]
                        length+=1
                    else:
                        counter[val][0]+=1
                        
            if length<self.gameboard.N:
                return (assignedVar, False)
                        
 
            for k,v in counter.items():
                if v[0] == 1:
                    if not v[1].isAssigned() and v[1].getDomain().contains(k):
                        self.trail.push(v[1])
                        v[1].assignValue(k)
                        assignedVar[v[1]]=k
            
        
        return (assignedVar, self.network.isConsistent())

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return False

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        unassignedVars = []
        # Getting all the unassigned variables
        for var in self.network.getVariables():
            if not var.isAssigned():   
                unassignedVars.append(var)
        if len(unassignedVars) != 0:
            minValues = unassignedVars[0].domain.size()   # initial min value
            mrv = None                                    # initial mrv
            # check number of values in the domain of each unassigned variable
            # and get the mrv variable
            for uv in unassignedVars:
                if uv.domain.size() <= minValues:
                    minValues = uv.domain.size()
                    mrv = uv
            return mrv
        else:
            return None

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with the smallest domain and affecting the most unassigned neighbors.
                If there are multiple variables that have the same smallest domain with the same number of unassigned neighbors, add them to the list of Variables.
                If there is only one variable, return the list of size 1 containing that variable.
    """
    def MRVwithTieBreaker ( self ):
        unassignedVars = []
        # Getting all the unassigned variables
        for var in self.network.getVariables():
            if not var.isAssigned():   
                unassignedVars.append(var)
        """
        if len(unassignedVars) != 0:
            minValues = unassignedVars[0].domain.size()   # initial min value
            for uv in unassignedVars:
                if uv.domain.size() < minValues:
                    minValues = uv.domain.size()

            minDomainList = [uv for uv in unassignedVars if uv.domain.size() == minValues]

            tempDict = dict.fromkeys(minDomainList, 0)

            for var in minDomainList:
                for neighbor in self.network.getNeighborsOfVariable(var):
                    if not neighbor.isAssigned():
                        tempDict[var]+=1

            return [keys for keys, value in tempDict.items() if value == max(tempDict.values())]
            
            tempList = [0 for _ in range(len(minDomainList))]
            for i in range(len(minDomainList)):
                for neighbor in self.network.getNeighborsOfVariable(minDomainList[i]):
                    if not neighbor.isAssigned():
                        tempList[i]+=1
            max_value = max(tempList)
            index_value = [i for i in range(len(tempList)) if tempList[i] == max_value]
        
            return [minDomainList[i] for i in index_value]

            """
        minDomainList = []
        neighborsList = []
        minFound = False

        if len(unassignedVars) != 0:
            minValues = unassignedVars[0].domain.size()   # initial min value
            for uv in unassignedVars:
                if uv.domain.size() > minValues:
                    continue
                elif uv.domain.size() == minValues:
                    minDomainList.append(uv)
                elif uv.domain.size() < minValues:
                    minDomainList.clear()
                    minDomainList.append(uv)
                    minValues = uv.domain.size()
                    minFound = True
                if minFound:
                    neighborsList.clear()
                    minFound = False
                count = 0
                for neighbor in self.network.getNeighborsOfVariable(uv):
                    if not neighbor.isAssigned():
                        count+=1
                neighborsList.append(count)

            max_value = max(neighborsList)
            index_value = [i for i in range(len(neighborsList)) if neighborsList[i] == max_value]
        
            return [minDomainList[i] for i in index_value]

        else:
            return [None]

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        result=dict.fromkeys(v.domain.values, 0)

        for neighbor in self.network.getNeighborsOfVariable(v):
            for value in neighbor.domain.values:
                if value in v.domain.values:
                    result[value]+=1

        return [value[0] for value in sorted(result.items(),key=lambda x:x[1])]

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self, time_left=600):
        if time_left <= 60:
            return -1

        start_time = time.time()
        if self.hassolution:
            return 0

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            # Success
            self.hassolution = True
            return 0

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recur
            if self.checkConsistency():
                elapsed_time = time.time() - start_time 
                new_start_time = time_left - elapsed_time
                if self.solve(time_left=new_start_time) == -1:
                    return -1
                
            # If this assignment succeeded, return
            if self.hassolution:
                return 0

            # Otherwise backtrack
            self.trail.undo()
        
        return 0

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()[1]

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()[1]

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()[0]

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
