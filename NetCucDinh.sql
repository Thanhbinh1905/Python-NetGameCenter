
SELECT Seats.SeatID, Computers.ComputerID
FROM Seats
LEFT JOIN Computers ON Seats.ComputerID = Computers.ComputerID

CREATE DATABASE NetCucDinh;
GO

USE NetCucDinh;
GO

SELECT * FROM Users WHERE Username = 'hehe' AND Password = '123'

CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(50) NOT NULL UNIQUE,
    Password NVARCHAR(255) NOT NULL, 
	Fullname NVARCHAR(50),
	Phone INT,
	Permission INT NOT NULL DEFAULT 0

);
GO

INSERT INTO Users (Username, Password, Permission) VALUES ('admin', 'admin', 1);

CREATE TABLE Computers (
    ComputerID INT PRIMARY KEY IDENTITY(1,1),
    Configurations NVARCHAR(MAX)
);
GO

INSERT INTO Computers 
VALUES
(N'Processor: Intel Core i7
RAM: 16GB
Storage: 512GB SSD
Graphics: NVIDIA GeForce RTX 3070'),
(N'Processor: AMD Ryzen 9
RAM: 32GB
Storage: 1TB SSD
Graphics: AMD Radeon RX 6800 XT'),
(N'Processor: Intel Core i9
RAM: 64GB
Storage: 2TB SSD + 4TB HDD
Graphics: NVIDIA GeForce RTX 3090');
GO



DECLARE @Counter INT = 1;

WHILE @Counter <= 50
BEGIN
    IF @Counter <= 20
    BEGIN
        INSERT INTO Seats (SeatID, ComputerID)
        VALUES (@Counter, 1);
    END
    ELSE IF @Counter <= 40
    BEGIN
        INSERT INTO Seats (SeatID, ComputerID)
        VALUES (@Counter, 2);
    END
    ELSE
    BEGIN
        INSERT INTO Seats (SeatID, ComputerID)
        VALUES (@Counter, 3);
    END

    SET @Counter = @Counter + 1;
END;

CREATE TABLE Seats (
    SeatID INT PRIMARY KEY,
    ComputerID INT,
    FOREIGN KEY (ComputerID) REFERENCES Computers(ComputerID)
);
GO

CREATE TABLE Usage (
    UsageID INT PRIMARY KEY IDENTITY(1,1),
    SeatID INT NOT NULL,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME,
	IsActive BIT NOT NULL DEFAULT 0,
    FOREIGN KEY (SeatID) REFERENCES Seats(SeatID),
);
GO
CREATE TABLE Payments (
    PaymentID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NOT NULL,
    UsageID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentTime DATETIME NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (UsageID) REFERENCES Usage(UsageID)
);
GO

CREATE TABLE Revenue (
    RevenueID INT PRIMARY KEY IDENTITY(1,1),
    Date DATE NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL
);
GO

CREATE PROCEDURE UpdateRevenueByDate
AS
BEGIN
    -- Declare a variable to store the current date
    DECLARE @CurrentDate DATE = CAST(GETDATE() AS DATE);

    -- Calculate the total amount for the current date
    DECLARE @TotalAmount DECIMAL(10, 2);
    SELECT @TotalAmount = SUM(Amount)
    FROM Payments
    WHERE CAST(PaymentTime AS DATE) = @CurrentDate;

    -- If there is no payment for the current date, set the total amount to 0
    IF @TotalAmount IS NULL
        SET @TotalAmount = 0;

    -- Check if there is already a record for the current date in the Revenue table
    IF EXISTS (SELECT 1 FROM Revenue WHERE Date = @CurrentDate)
    BEGIN
        -- Update the existing record
        UPDATE Revenue
        SET TotalAmount = @TotalAmount
        WHERE Date = @CurrentDate;
    END
    ELSE
    BEGIN
        -- Insert a new record
        INSERT INTO Revenue (Date, TotalAmount)
        VALUES (@CurrentDate, @TotalAmount);
    END
END;
GO

SELECT UserID, Username FROM Users

SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = 'NetCucDinh';

SELECT Seats.SeatID, Computers.ComputerID, Computers.Configurations, Usage.StartTime,
       CASE 
           WHEN Usage.EndTime IS NULL AND Usage.IsActive = 1 THEN 'Active' 
           ELSE 'Inactive' 
       END AS Status
FROM Seats
LEFT JOIN Computers ON Seats.ComputerID = Computers.ComputerID
LEFT JOIN Usage ON Seats.SeatID = Usage.SeatID

SELECT Seats.SeatID, Computers.ComputerID, Computers.Configurations, Usage.StartTime,
               CASE 
                   WHEN Usage.EndTime IS NULL AND Usage.IsActive = 1 THEN 'Active' 
                   ELSE 'Inactive' 
               END AS Status
        FROM Seats
        LEFT JOIN Computers ON Seats.ComputerID = Computers.ComputerID
        LEFT JOIN Usage ON Seats.SeatID = Usage.SeatID
        WHERE Seats.SeatID = 1

DELETE FROM Seats;

SELECT TOP 1 UsageID
FROM Usage
WHERE SeatID = 5 AND IsActive=1
ORDER BY ABS(DATEDIFF(second, StartTime, GETDATE()))

UPDATE Usage SET IsActive=0 WHERE SeatID=1 AND IsActive=1 AND EndTime = NULL

Select * from Usage

SELECT s.SeatID, 
       c.Configurations, 
       CASE
           WHEN u.IsActive = 1 THEN 'Active'
           ELSE 'Inactive'
       END AS Status,
       u.StartTime
FROM Seats s
INNER JOIN Computers c ON s.ComputerID = c.ComputerID
LEFT JOIN Usage u ON s.SeatID = u.SeatID AND u.IsActive = 1;


DELETE FROM Usage;

SELECT TOP 5
    s.SeatID,
    COUNT(u.UsageID) AS UsageCount
FROM 
    Seats s
LEFT JOIN 
    Usage u ON s.SeatID = u.SeatID
GROUP BY 
    s.SeatID
ORDER BY 
    UsageCount DESC;

SELECT Date, TotalAmount FROM Revenue

SELECT 
    SUM(Amount) AS TotalAmount
FROM 
    Payments
WHERE 
    CAST(PaymentTime AS DATE) = CAST(GETDATE() AS DATE);

SELECT COUNT(*) AS ActiveUsageCount
FROM Usage
WHERE IsActive = 1;

SELECT * FROM Computers

DELETE FROM Computers WHERE ComputerID = 4

SELECT s.SeatID, c.Configurations 
FROM Seats s
INNER JOIN Computers c ON s.ComputerID = c.ComputerID

SELECT UserID, Username, Fullname, Phone, Permission FROM Users

UPDATE Users SET Password = '123', Permission = 1 Where Username = 'admin'